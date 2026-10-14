package com.modelgate.service;

import com.modelgate.config.OpenRouterProperties;
import com.modelgate.dto.OpenRouterModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.*;

@Service
public class OpenRouterService {

    private static final Logger log = LoggerFactory.getLogger(OpenRouterService.class);

    private final RestClient restClient;
    private final OpenRouterProperties openRouterProperties;

    public OpenRouterService(RestClient restClient, OpenRouterProperties openRouterProperties) {
        this.restClient = restClient;
        this.openRouterProperties = openRouterProperties;
    }

    @SuppressWarnings("unchecked")
    public List<OpenRouterModel> browseCatalog(String query) {
        try {
            Map<String, Object> response = restClient.get()
                    .uri("/models")
                    .header("Authorization", "Bearer " + openRouterProperties.getApiKey())
                    .retrieve()
                    .body(Map.class);

            if (response == null) {
                return List.of();
            }

            List<Map<String, Object>> data = (List<Map<String, Object>>) response.getOrDefault("data", List.of());
            List<OpenRouterModel> models = new ArrayList<>();
            String q = query != null ? query.toLowerCase() : "";

            for (Map<String, Object> m : data) {
                String modelId = String.valueOf(m.getOrDefault("id", ""));
                String name = String.valueOf(m.getOrDefault("name", modelId));
                Map<String, Object> pricing = (Map<String, Object>) m.getOrDefault("pricing", Map.of());

                if (!q.isEmpty()
                        && !name.toLowerCase().contains(q)
                        && !modelId.toLowerCase().contains(q)) {
                    continue;
                }

                double promptCost = parseCost(pricing.get("prompt"));
                double completionCost = parseCost(pricing.get("completion"));

                OpenRouterModel model = new OpenRouterModel();
                model.setId(modelId);
                model.setName(name);
                model.setContextLength(m.containsKey("context_length")
                        ? ((Number) m.get("context_length")).intValue() : 0);
                model.setCostPerMInput(Math.round(promptCost * 10000.0) / 10000.0);
                model.setCostPerMOutput(Math.round(completionCost * 10000.0) / 10000.0);
                model.setProvider(modelId.contains("/")
                        ? modelId.substring(0, modelId.indexOf("/"))
                        : "unknown");
                models.add(model);
            }

            models.sort(Comparator.comparing(OpenRouterModel::getName, String.CASE_INSENSITIVE_ORDER));
            return models.size() > 100 ? models.subList(0, 100) : models;
        } catch (Exception e) {
            log.error("Failed to fetch OpenRouter catalog: {}", e.getMessage());
            return List.of();
        }
    }

    private double parseCost(Object value) {
        if (value == null) {
            return 0.0;
        }
        try {
            return Double.parseDouble(String.valueOf(value)) * 1_000_000;
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }
}
