package com.modelgate.service;

import com.modelgate.domain.CustomerProfile;
import com.modelgate.domain.ModelInfo;
import com.modelgate.domain.RoutingDecision;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class RoutingEngineService {

    private static final Logger log = LoggerFactory.getLogger(RoutingEngineService.class);

    private static final Map<String, Integer> TIER_QUALITY_SCORES = Map.of(
            "simple", 1, "medium", 2, "complex", 3
    );

    private static final Map<String, String> TIER_ESCALATION = Map.of(
            "simple", "medium", "medium", "complex", "complex", "complex"
    );

    private static final Map<String, List<String>> DEFAULT_CANDIDATES = Map.of(
            "simple", List.of("gpt-4o-mini", "claude-haiku", "gemini-2.0-flash"),
            "medium", List.of("claude-sonnet", "gpt-4o"),
            "complex", List.of("gemini-2.5-pro", "claude-sonnet")
    );

    private final PromptClassifier promptClassifier;
    private final ModelCatalogService modelCatalogService;

    public RoutingEngineService(PromptClassifier promptClassifier, ModelCatalogService modelCatalogService) {
        this.promptClassifier = promptClassifier;
        this.modelCatalogService = modelCatalogService;
    }

    public RoutingDecision route(CustomerProfile profile, String prompt, String tierOverride) {
        String classification = tierOverride != null ? tierOverride : promptClassifier.classifyPrompt(prompt);

        List<String> candidates = new ArrayList<>(profile.getRoutingPreferences().getOrDefault(classification, List.of()));
        if (candidates.isEmpty()) {
            candidates = new ArrayList<>(getDefaultCandidates(classification));
        }

        Set<String> enabledModels = modelCatalogService.getEnabledModels();

        Map<String, String> eliminated = new LinkedHashMap<>();
        List<String> validCandidates = new ArrayList<>();

        for (String modelName : candidates) {
            if (!enabledModels.contains(modelName)) {
                eliminated.put(modelName, "model disabled by admin");
                continue;
            }

            ModelInfo modelInfo = modelCatalogService.getModelInfo(modelName);
            if (modelInfo == null) {
                eliminated.put(modelName, "model not found in registry");
                continue;
            }

            String provider = modelInfo.getProvider();

            if (profile.getConstraints().getForbiddenProviders().contains(provider)) {
                eliminated.put(modelName, "provider '" + provider + "' forbidden by contract");
                continue;
            }

            if (!profile.getConstraints().getAllowedProviders().isEmpty()
                    && !profile.getConstraints().getAllowedProviders().contains(provider)) {
                eliminated.put(modelName, "provider '" + provider + "' not in allowed list");
                continue;
            }

            if (!"any".equals(profile.getConstraints().getRegion())) {
                String requiredRegion = profile.getConstraints().getRegion().replace("-only", "");
                if (!modelInfo.getRegions().contains(requiredRegion)) {
                    eliminated.put(modelName, "region '" + requiredRegion + "' not supported");
                    continue;
                }
            }

            validCandidates.add(modelName);
        }

        if (validCandidates.isEmpty()) {
            String nextTier = TIER_ESCALATION.getOrDefault(classification, "complex");
            List<String> escalationCandidates = profile.getRoutingPreferences().getOrDefault(nextTier, List.of());
            for (String modelName : escalationCandidates) {
                if (!eliminated.containsKey(modelName) && enabledModels.contains(modelName)) {
                    ModelInfo modelInfo = modelCatalogService.getModelInfo(modelName);
                    if (modelInfo != null && passesPolicy(modelInfo, profile)) {
                        validCandidates.add(modelName);
                    }
                }
            }
        }

        if (validCandidates.isEmpty()) {
            for (Map.Entry<String, ModelInfo> entry : modelCatalogService.getActiveCatalog().entrySet()) {
                if (enabledModels.contains(entry.getKey()) && passesPolicy(entry.getValue(), profile)) {
                    validCandidates.add(entry.getKey());
                    break;
                }
            }
        }

        if (validCandidates.isEmpty()) {
            validCandidates.add("gpt-4o-mini");
        }

        String best = scoreAndSelect(validCandidates, profile);
        ModelInfo bestInfo = modelCatalogService.getModelInfo(best);
        if (bestInfo == null) {
            bestInfo = new ModelInfo();
        }

        List<String> reasonParts = new ArrayList<>();
        reasonParts.add(classification + " complexity");
        reasonParts.add((bestInfo.getProvider() != null ? bestInfo.getProvider() : "?") + "/" + best + " selected");

        int latency = bestInfo.getAvgLatencyMs();
        int target = profile.getPerformance().getLatencyTargetMs();
        if (latency <= target) {
            reasonParts.add("meets " + target + "ms latency target (" + latency + "ms avg)");
        } else {
            reasonParts.add("latency " + latency + "ms exceeds " + target + "ms target (best available)");
        }

        reasonParts.add("objective: " + profile.getObjective());
        String reason = String.join("; ", reasonParts);

        RoutingDecision decision = new RoutingDecision();
        decision.setSelectedProvider(bestInfo.getProvider() != null ? bestInfo.getProvider() : "unknown");
        decision.setSelectedModel(best);
        decision.setClassification(classification);
        decision.setReason(reason);
        decision.setCandidatesConsidered(candidates);
        decision.setCandidatesEliminated(eliminated);
        return decision;
    }

    private boolean passesPolicy(ModelInfo modelInfo, CustomerProfile profile) {
        String provider = modelInfo.getProvider();
        if (profile.getConstraints().getForbiddenProviders().contains(provider)) {
            return false;
        }
        if (!profile.getConstraints().getAllowedProviders().isEmpty()
                && !profile.getConstraints().getAllowedProviders().contains(provider)) {
            return false;
        }
        if (!"any".equals(profile.getConstraints().getRegion())) {
            String requiredRegion = profile.getConstraints().getRegion().replace("-only", "");
            if (!modelInfo.getRegions().contains(requiredRegion)) {
                return false;
            }
        }
        return true;
    }

    private String scoreAndSelect(List<String> candidates, CustomerProfile profile) {
        Map<String, Double> scores = new LinkedHashMap<>();

        for (String name : candidates) {
            ModelInfo info = modelCatalogService.getModelInfo(name);
            if (info == null) {
                continue;
            }

            double score = 0.0;

            if ("low_latency".equals(profile.getObjective())) {
                score += (1.0 / Math.max(info.getAvgLatencyMs(), 1)) * 10000;
            } else if ("low_cost".equals(profile.getObjective())) {
                score += (1.0 / Math.max(info.getCostPerMInput(), 0.00001)) * 0.01;
            } else if ("high_quality".equals(profile.getObjective())) {
                score += TIER_QUALITY_SCORES.getOrDefault(info.getTier(), 1) * 10;
            }

            if (info.getAvgLatencyMs() <= profile.getPerformance().getLatencyTargetMs()) {
                score += 5;
            }

            if ("high".equals(profile.getPerformance().getCostSensitivity())) {
                score += (1.0 / Math.max(info.getCostPerMInput(), 0.00001)) * 0.001;
            }

            scores.put(name, score);
        }

        if (scores.isEmpty()) {
            return candidates.get(0);
        }

        return scores.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(candidates.get(0));
    }

    private List<String> getDefaultCandidates(String tier) {
        return DEFAULT_CANDIDATES.getOrDefault(tier, List.of("gpt-4o-mini"));
    }
}
