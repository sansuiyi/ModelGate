package com.modelgate.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.modelgate.common.ModelProviderException;
import com.modelgate.config.OpenRouterProperties;
import com.modelgate.domain.CustomerProfile;
import com.modelgate.domain.RoutingDecision;
import com.modelgate.dto.ChatCompletionRequest;
import com.modelgate.util.SlugUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.util.*;

@Service
public class ProxyService {

    private static final Logger log = LoggerFactory.getLogger(ProxyService.class);

    private static final Map<String, String> TIER_MODEL_MAP = Map.of(
            "modelgate-simple", "simple",
            "modelgate-medium", "medium",
            "modelgate-complex", "complex"
    );

    private static final Map<String, String> TIER_DESCRIPTIONS = Map.of(
            "simple", "Fast, cost-efficient responses for routine queries",
            "medium", "Balanced quality and speed for standard tasks",
            "complex", "Maximum capability for complex reasoning and analysis"
    );

    private final CustomerService customerService;
    private final RoutingEngineService routingEngineService;
    private final ModelCatalogService modelCatalogService;
    private final StatsService statsService;
    private final RestClient restClient;
    private final OpenRouterProperties openRouterProperties;
    private final ObjectMapper objectMapper;

    public ProxyService(CustomerService customerService,
                        RoutingEngineService routingEngineService,
                        ModelCatalogService modelCatalogService,
                        StatsService statsService,
                        RestClient restClient,
                        OpenRouterProperties openRouterProperties,
                        ObjectMapper objectMapper) {
        this.customerService = customerService;
        this.routingEngineService = routingEngineService;
        this.modelCatalogService = modelCatalogService;
        this.statsService = statsService;
        this.restClient = restClient;
        this.openRouterProperties = openRouterProperties;
        this.objectMapper = objectMapper;
    }

    public Map<String, Object> listModels(String customerId) {
        CustomerProfile profile = customerService.getCustomerOrThrow(customerId);

        long created = 1711000000L;
        if (profile.getCreatedAt() != null && !profile.getCreatedAt().isEmpty()) {
            try {
                created = Instant.parse(profile.getCreatedAt()).getEpochSecond();
            } catch (Exception e) {
                // use default
            }
        }

        List<Map<String, Object>> models = new ArrayList<>();

        Map<String, Object> autoModel = new LinkedHashMap<>();
        autoModel.put("id", "auto");
        autoModel.put("object", "model");
        autoModel.put("created", created);
        autoModel.put("owned_by", "modelgate");
        autoModel.put("description", "Automatic routing — ModelGate classifies your prompt and selects the optimal tier");
        models.add(autoModel);

        for (String tier : profile.getRoutingPreferences().keySet()) {
            Map<String, Object> model = new LinkedHashMap<>();
            model.put("id", "modelgate-" + tier);
            model.put("object", "model");
            model.put("created", created);
            model.put("owned_by", "modelgate");
            model.put("description", TIER_DESCRIPTIONS.getOrDefault(tier, "Service tier: " + tier));
            models.add(model);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("object", "list");
        result.put("data", models);
        return result;
    }

    @SuppressWarnings("unchecked")
    public ProxyResult chatCompletions(String customerId, ChatCompletionRequest request) {
        CustomerProfile profile = customerService.getCustomerOrThrow(customerId);

        String userPrompt = "";
        if (request.getMessages() != null) {
            for (int i = request.getMessages().size() - 1; i >= 0; i--) {
                Map<String, Object> msg = request.getMessages().get(i);
                if ("user".equals(msg.get("role"))) {
                    userPrompt = String.valueOf(msg.getOrDefault("content", ""));
                    break;
                }
            }
        }

        if (userPrompt.isEmpty()) {
            throw new IllegalArgumentException("No user message found");
        }

        String tierOverride = TIER_MODEL_MAP.get(request.getModel());

        long classifyStart = System.nanoTime();
        RoutingDecision decision = routingEngineService.route(profile, userPrompt, tierOverride);
        int classifyMs = (int) ((System.nanoTime() - classifyStart) / 1_000_000);
        String openrouterModel = modelCatalogService.getOpenRouterId(decision.getSelectedModel());

        String status = "success";
        int ttftMs = 0;
        long startTime = System.nanoTime();

        Map<String, Object> requestBody = new LinkedHashMap<>();
        requestBody.put("model", openrouterModel);
        requestBody.put("messages", request.getMessages());
        requestBody.put("temperature", request.getTemperature());
        if (request.getMaxTokens() != null) {
            requestBody.put("max_tokens", request.getMaxTokens());
        }

        Map<String, Object> result;
        try {
            result = restClient.post()
                    .uri("/chat/completions")
                    .header("Authorization", "Bearer " + openRouterProperties.getApiKey())
                    .header("Content-Type", "application/json")
                    .body(requestBody)
                    .retrieve()
                    .body(Map.class);

            ttftMs = (int) ((System.nanoTime() - startTime) / 1_000_000);
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            status = "error";
            int code = e.getStatusCode().value();
            log.error("OpenRouter error: {} {}", code, e.getResponseBodyAsString());
            throw new ModelProviderException("Model provider error: " + code, e);
        } catch (Exception e) {
            status = "error";
            log.error("OpenRouter request failed: {}", e.getMessage());
            throw new ModelProviderException("Failed to reach model provider", e);
        }

        int latencyMs = (int) ((System.nanoTime() - startTime) / 1_000_000);

        Map<String, Object> usage = result != null ? (Map<String, Object>) result.getOrDefault("usage", Map.of()) : Map.of();
        int inputTokens = usage.containsKey("prompt_tokens")
                ? ((Number) usage.get("prompt_tokens")).intValue()
                : userPrompt.split("\\s+").length * 2;
        int outputTokens = usage.containsKey("completion_tokens")
                ? ((Number) usage.get("completion_tokens")).intValue()
                : 100;
        int totalTokens = inputTokens + outputTokens;

        double cost = modelCatalogService.estimateCost(decision.getSelectedModel(), inputTokens, outputTokens);

        Map<String, Object> logEntry = new LinkedHashMap<>();
        logEntry.put("customer_id", customerId);
        logEntry.put("timestamp", Instant.now().toString());
        logEntry.put("prompt_preview", userPrompt.length() > 200 ? userPrompt.substring(0, 200) : userPrompt);
        logEntry.put("classification", decision.getClassification());
        logEntry.put("selected_provider", decision.getSelectedProvider());
        logEntry.put("selected_model", decision.getSelectedModel());
        logEntry.put("reason", decision.getReason());
        logEntry.put("latency_ms", latencyMs);
        logEntry.put("estimated_cost", cost);
        logEntry.put("tokens_used", totalTokens);
        logEntry.put("input_tokens", inputTokens);
        logEntry.put("output_tokens", outputTokens);
        logEntry.put("ttft_ms", ttftMs);
        logEntry.put("status", status);
        logEntry.put("candidates_considered", decision.getCandidatesConsidered());
        logEntry.put("candidates_eliminated", decision.getCandidatesEliminated());
        statsService.saveRequestLog(logEntry);

        Map<String, Object> routingMeta = new LinkedHashMap<>();
        routingMeta.put("selected_provider", decision.getSelectedProvider());
        routingMeta.put("selected_model", decision.getSelectedModel());
        routingMeta.put("classification", decision.getClassification());
        routingMeta.put("reason", decision.getReason());
        routingMeta.put("candidates_considered", decision.getCandidatesConsidered());
        routingMeta.put("candidates_eliminated", decision.getCandidatesEliminated());
        routingMeta.put("latency_ms", latencyMs);
        routingMeta.put("ttft_ms", ttftMs);
        routingMeta.put("classify_ms", classifyMs);
        routingMeta.put("cost", cost);
        routingMeta.put("input_tokens", inputTokens);
        routingMeta.put("output_tokens", outputTokens);

        Map<String, String> headers = new LinkedHashMap<>();
        try {
            headers.put("X-Routing-Decision", objectMapper.writeValueAsString(routingMeta));
        } catch (Exception e) {
            headers.put("X-Routing-Decision", "{}");
        }
        headers.put("X-Model-Used", decision.getSelectedModel());
        headers.put("X-Classification", decision.getClassification());
        headers.put("X-Latency-Ms", String.valueOf(latencyMs));
        headers.put("X-TTFT-Ms", String.valueOf(ttftMs));
        headers.put("X-Classify-Ms", String.valueOf(classifyMs));
        headers.put("X-Cost", String.valueOf(cost));

        return new ProxyResult(result, headers);
    }

    public static class ProxyResult {
        private final Object body;
        private final Map<String, String> headers;

        public ProxyResult(Object body, Map<String, String> headers) {
            this.body = body;
            this.headers = headers;
        }

        public Object getBody() {
            return body;
        }

        public Map<String, String> getHeaders() {
            return headers;
        }
    }
}
