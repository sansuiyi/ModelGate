package com.modelgate.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.modelgate.config.DataProperties;
import com.modelgate.config.OpenRouterProperties;
import com.modelgate.domain.CustomerProfile;
import com.modelgate.domain.ModelInfo;
import com.modelgate.util.SlugUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class ContractExtractionService {

    private static final Logger log = LoggerFactory.getLogger(ContractExtractionService.class);

    private static final String EXTRACTION_PROMPT = """
            Extract an AI routing profile from this contract. Output ONLY raw JSON — no markdown, no explanation.

            <contract>
            {contract_text}
            </contract>

            <custom_instructions>
            {custom_instructions}
            </custom_instructions>

            <environment>
            Providers in this environment: {available_providers}

            Models by tier:
            {models_by_tier}
            </environment>

            Output this exact JSON schema:
            {{
              "customer_name": "<short company name>",
              "use_case": "<3-6 word description>",
              "objective": "<one of: low_latency | high_quality | low_cost>",
              "constraints": {{
                "region": "<one of: EU-only | US-only | any>",
                "privacy_tier": "<one of: low | standard | high>",
                "forbidden_providers": [],
                "allowed_providers": []
              }},
              "performance": {{
                "latency_target_ms": <integer>,
                "cost_sensitivity": "<one of: low | medium | high>"
              }},
              "routing_preferences": {{
                "simple": ["<model_name>", "<model_name>"],
                "medium": ["<model_name>", "<model_name>"],
                "complex": ["<model_name>", "<model_name>"]
              }},
              "warnings": [
                {{
                  "type": "<one of: provider_gap | model_gap | region_gap | missing_field | contract_ambiguity>",
                  "severity": "<one of: critical | warning | info>",
                  "message": "<short actionable message>"
                }}
              ]
            }}

            RULES:

            1. TERSE VALUES:
               - customer_name: company name only
               - use_case: max 6 words

            2. PROVIDERS vs MODELS are DIFFERENT things:
               - forbidden_providers / allowed_providers -> PROVIDER names: {available_providers}
               - routing_preferences -> MODEL names from the tier lists above
               - NEVER mix them up

            3. PROVIDERS:
               - forbidden_providers: only if contract EXPLICITLY bans a provider (e.g. "China-based" -> ["deepseek"])
               - allowed_providers: only if contract EXPLICITLY restricts to specific providers. Empty [] means all allowed.

            4. ROUTING PREFERENCES — MUST respect model tiers:
               - The models above are grouped by tier (simple/medium/complex). This is their CONFIGURED tier.
               - routing_preferences["simple"] MUST only contain models from the "simple" tier list
               - routing_preferences["medium"] MUST only contain models from the "medium" tier list
               - routing_preferences["complex"] MUST only contain models from the "complex" tier list
               - Pick 1-2 models per tier that are compatible with the contract constraints (allowed providers, region)
               - Do NOT put a medium-tier model into the complex routing preference or vice versa

            5. LATENCY: use contract value if specified, else default: low_latency=1000, high_quality=5000, low_cost=3000

            6. WARNINGS — structured objects, only for actionable issues:
               - provider_gap: contract requires a provider not deployed (e.g. "Contract requires Anthropic but no anthropic models in environment")
               - model_gap: a tier has no compatible models after applying constraints
               - region_gap: required region not supported by available models
               - missing_field: contract doesn't specify something important (latency, region, etc.)
               - contract_ambiguity: contract is unclear about a routing-relevant requirement
               - Do NOT warn about compliance, legal, auditing, retention, or anything outside AI routing
               - severity "critical" = blocks routing, "warning" = degraded routing, "info" = FYI""";

    private final RestClient restClient;
    private final OpenRouterProperties openRouterProperties;
    private final ModelCatalogService modelCatalogService;
    private final DataProperties dataProperties;
    private final ObjectMapper objectMapper;

    public ContractExtractionService(RestClient restClient,
                                     OpenRouterProperties openRouterProperties,
                                     ModelCatalogService modelCatalogService,
                                     DataProperties dataProperties,
                                     ObjectMapper objectMapper) {
        this.restClient = restClient;
        this.openRouterProperties = openRouterProperties;
        this.modelCatalogService = modelCatalogService;
        this.dataProperties = dataProperties;
        this.objectMapper = objectMapper;
    }

    public CustomerProfile extractProfile(String customerName, String contractText, String customInstructions) {
        Map<String, ModelInfo> catalog = modelCatalogService.getActiveCatalog();

        Map<String, List<String>> tiers = new LinkedHashMap<>();
        tiers.put("simple", new ArrayList<>());
        tiers.put("medium", new ArrayList<>());
        tiers.put("complex", new ArrayList<>());

        for (Map.Entry<String, ModelInfo> entry : catalog.entrySet()) {
            String name = entry.getKey();
            ModelInfo info = entry.getValue();
            String tier = info.getTier() != null ? info.getTier() : "medium";
            String desc = String.format("%s (provider: %s, $%.2f/MTok, %dms)",
                    name, info.getProvider(), info.getCostPerMInput(), info.getAvgLatencyMs());
            tiers.computeIfAbsent(tier, k -> new ArrayList<>()).add(desc);
        }

        List<String> lines = new ArrayList<>();
        for (String tier : List.of("simple", "medium", "complex")) {
            List<String> list = tiers.getOrDefault(tier, List.of());
            String joined = list.isEmpty() ? "none" : String.join(", ", list);
            lines.add("  " + tier + ": " + joined);
        }
        String modelsByTier = String.join("\n", lines);

        List<String> providers = catalog.values().stream()
                .map(ModelInfo::getProvider)
                .filter(Objects::nonNull)
                .distinct()
                .sorted()
                .collect(Collectors.toList());
        String availableProviders = String.join(", ", providers);

        String prompt = EXTRACTION_PROMPT
                .replace("{contract_text}", contractText)
                .replace("{custom_instructions}", customInstructions != null && !customInstructions.isEmpty() ? customInstructions : "None")
                .replace("{models_by_tier}", modelsByTier)
                .replace("{available_providers}", availableProviders);

        try {
            Map<String, Object> requestBody = new LinkedHashMap<>();
            requestBody.put("model", openRouterProperties.getExtractionModel());
            requestBody.put("messages", List.of(Map.of("role", "user", "content", prompt)));
            requestBody.put("temperature", 0.0);
            requestBody.put("max_tokens", 1200);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restClient.post()
                    .uri("/chat/completions")
                    .header("Authorization", "Bearer " + openRouterProperties.getApiKey())
                    .header("Content-Type", "application/json")
                    .body(requestBody)
                    .retrieve()
                    .body(Map.class);

            if (response == null) {
                throw new RuntimeException("Empty response from OpenRouter");
            }

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices == null || choices.isEmpty()) {
                throw new RuntimeException("No choices in response");
            }
            @SuppressWarnings("unchecked")
            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            String content = ((String) message.get("content")).trim();

            if (content.startsWith("```")) {
                if (content.contains("\n")) {
                    content = content.substring(content.indexOf("\n") + 1);
                } else {
                    content = content.substring(3);
                }
                if (content.endsWith("```")) {
                    content = content.substring(0, content.length() - 3);
                }
                content = content.trim();
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> profileData = objectMapper.readValue(content, Map.class);

            CustomerProfile profile = buildProfile(customerName, profileData);
            return profile;

        } catch (Exception e) {
            log.error("Extraction failed: {}", e.getMessage());
            CustomerProfile fallback = loadFallback(customerName);
            if (fallback != null) {
                log.info("Using fallback profile for {}", customerName);
                return fallback;
            }
            throw new RuntimeException("Extraction failed and no fallback available: " + e.getMessage(), e);
        }
    }

    @SuppressWarnings("unchecked")
    private CustomerProfile buildProfile(String customerName, Map<String, Object> data) {
        String customerId = SlugUtil.slugify(customerName);

        CustomerProfile profile = new CustomerProfile();
        profile.setCustomerId(customerId);
        profile.setCustomerName((String) data.getOrDefault("customer_name", customerName));
        profile.setUseCase((String) data.getOrDefault("use_case", "general"));
        profile.setObjective((String) data.getOrDefault("objective", "low_cost"));

        Map<String, Object> constraintsData = (Map<String, Object>) data.getOrDefault("constraints", new LinkedHashMap<>());
        profile.setConstraints(objectMapper.convertValue(constraintsData, com.modelgate.domain.CustomerConstraints.class));

        Map<String, Object> performanceData = (Map<String, Object>) data.getOrDefault("performance", new LinkedHashMap<>());
        profile.setPerformance(objectMapper.convertValue(performanceData, com.modelgate.domain.CustomerPerformance.class));

        Map<String, List<String>> routingPrefs = (Map<String, List<String>>) data.getOrDefault("routing_preferences",
                Map.of("simple", List.of("gpt-4o-mini"), "medium", List.of("claude-sonnet"), "complex", List.of("gemini-2.5-pro")));
        profile.setRoutingPreferences(routingPrefs);

        List<Object> warnings = (List<Object>) data.getOrDefault("warnings", new ArrayList<>());
        profile.setWarnings(warnings);

        profile.setCreatedAt(java.time.Instant.now().toString());
        return profile;
    }

    @SuppressWarnings("unchecked")
    private CustomerProfile loadFallback(String customerName) {
        String slug = SlugUtil.slugify(customerName);
        Path fallbackDir = Paths.get(dataProperties.getFallbackProfilesDir());

        if (!Files.isDirectory(fallbackDir)) {
            return null;
        }

        Path fallbackPath = fallbackDir.resolve(slug + ".json");
        if (Files.isReadable(fallbackPath)) {
            try {
                String json = Files.readString(fallbackPath);
                return objectMapper.readValue(json, CustomerProfile.class);
            } catch (Exception e) {
                log.warn("Failed to parse fallback file {}: {}", fallbackPath, e.getMessage());
            }
        }

        try (var stream = Files.list(fallbackDir)) {
            for (Path f : stream.filter(p -> p.toString().endsWith(".json")).toList()) {
                String stem = f.getFileName().toString().replace(".json", "");
                if (slug.contains(stem) || stem.contains(slug)) {
                    try {
                        String json = Files.readString(f);
                        return objectMapper.readValue(json, CustomerProfile.class);
                    } catch (Exception e) {
                        log.warn("Failed to parse fallback file {}: {}", f, e.getMessage());
                    }
                }
            }
        } catch (Exception e) {
            log.warn("Failed to list fallback profiles: {}", e.getMessage());
        }

        return null;
    }
}
