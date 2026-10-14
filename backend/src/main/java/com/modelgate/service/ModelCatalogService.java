package com.modelgate.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.modelgate.domain.ModelInfo;
import com.modelgate.dto.ModelCreate;
import com.modelgate.entity.GlobalModelEntity;
import com.modelgate.repository.GlobalModelRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class ModelCatalogService {

    private static final Logger log = LoggerFactory.getLogger(ModelCatalogService.class);

    private static final Map<String, ModelInfo> DEFAULT_MODELS;

    static {
        DEFAULT_MODELS = new LinkedHashMap<>();

        ModelInfo m = new ModelInfo();
        m.setProvider("anthropic");
        m.setOpenrouterId("anthropic/claude-3-5-haiku-20241022");
        m.setTier("simple");
        m.setCostPerMInput(0.80);
        m.setCostPerMOutput(4.00);
        m.setAvgLatencyMs(350);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(200000);
        m.setDescription("Fast, affordable model for simple tasks");
        DEFAULT_MODELS.put("claude-haiku", m);

        m = new ModelInfo();
        m.setProvider("openai");
        m.setOpenrouterId("openai/gpt-4o-mini");
        m.setTier("simple");
        m.setCostPerMInput(0.15);
        m.setCostPerMOutput(0.60);
        m.setAvgLatencyMs(400);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(128000);
        m.setDescription("Cost-effective model for basic queries");
        DEFAULT_MODELS.put("gpt-4o-mini", m);

        m = new ModelInfo();
        m.setProvider("anthropic");
        m.setOpenrouterId("anthropic/claude-sonnet-4");
        m.setTier("medium");
        m.setCostPerMInput(3.00);
        m.setCostPerMOutput(15.00);
        m.setAvgLatencyMs(900);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(200000);
        m.setDescription("Balanced model for moderate analysis");
        DEFAULT_MODELS.put("claude-sonnet", m);

        m = new ModelInfo();
        m.setProvider("openai");
        m.setOpenrouterId("openai/gpt-4o");
        m.setTier("medium");
        m.setCostPerMInput(2.50);
        m.setCostPerMOutput(10.00);
        m.setAvgLatencyMs(800);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(128000);
        m.setDescription("Strong general-purpose model");
        DEFAULT_MODELS.put("gpt-4o", m);

        m = new ModelInfo();
        m.setProvider("google");
        m.setOpenrouterId("google/gemini-2.0-flash-001");
        m.setTier("simple");
        m.setCostPerMInput(0.10);
        m.setCostPerMOutput(0.40);
        m.setAvgLatencyMs(300);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(1000000);
        m.setDescription("Ultra-fast, cheapest option for simple tasks");
        DEFAULT_MODELS.put("gemini-2.0-flash", m);

        m = new ModelInfo();
        m.setProvider("google");
        m.setOpenrouterId("google/gemini-2.5-pro-preview-06-05");
        m.setTier("complex");
        m.setCostPerMInput(2.50);
        m.setCostPerMOutput(15.00);
        m.setAvgLatencyMs(1500);
        m.setRegions(List.of("US", "EU"));
        m.setMaxContext(1000000);
        m.setDescription("Advanced reasoning for complex tasks");
        DEFAULT_MODELS.put("gemini-2.5-pro", m);

        m = new ModelInfo();
        m.setProvider("deepseek");
        m.setOpenrouterId("deepseek/deepseek-chat-v3-0324");
        m.setTier("medium");
        m.setCostPerMInput(0.30);
        m.setCostPerMOutput(0.80);
        m.setAvgLatencyMs(600);
        m.setRegions(List.of("CN", "US"));
        m.setMaxContext(128000);
        m.setDescription("Cost-effective Chinese provider model");
        DEFAULT_MODELS.put("deepseek-v3", m);
    }

    private final GlobalModelRepository globalModelRepository;
    private final ObjectMapper objectMapper;

    public ModelCatalogService(GlobalModelRepository globalModelRepository, ObjectMapper objectMapper) {
        this.globalModelRepository = globalModelRepository;
        this.objectMapper = objectMapper;
    }

    @Cacheable(value = "catalog", key = "'active'")
    public Map<String, ModelInfo> getActiveCatalog() {
        Map<String, ModelInfo> dbModels = getGlobalModelsFull();
        if (!dbModels.isEmpty()) {
            return dbModels;
        }
        return DEFAULT_MODELS;
    }

    public ModelInfo getModelInfo(String modelName) {
        return getActiveCatalog().get(modelName);
    }

    public String getOpenRouterId(String modelName) {
        ModelInfo info = getActiveCatalog().get(modelName);
        if (info != null) {
            return info.getOpenrouterId();
        }
        return modelName;
    }

    public List<String> getModelsForTier(String tier) {
        return getActiveCatalog().entrySet().stream()
                .filter(e -> tier.equals(e.getValue().getTier()))
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    public double estimateCost(String modelName, int inputTokens, int outputTokens) {
        ModelInfo info = getActiveCatalog().get(modelName);
        if (info == null) {
            return 0.0;
        }
        double inputCost = (inputTokens / 1_000_000.0) * info.getCostPerMInput();
        double outputCost = (outputTokens / 1_000_000.0) * info.getCostPerMOutput();
        return BigDecimal.valueOf(inputCost + outputCost)
                .setScale(8, RoundingMode.HALF_UP)
                .doubleValue();
    }

    public List<String> getAllProviders() {
        return getActiveCatalog().values().stream()
                .map(ModelInfo::getProvider)
                .distinct()
                .collect(Collectors.toList());
    }

    public List<String> getAllModelNames() {
        return new ArrayList<>(getActiveCatalog().keySet());
    }

    @Cacheable(value = "catalog", key = "'enabled'")
    public Set<String> getEnabledModels() {
        List<GlobalModelEntity> all = globalModelRepository.findAll();
        if (all.isEmpty()) {
            return new LinkedHashSet<>(DEFAULT_MODELS.keySet());
        }
        return all.stream()
                .filter(e -> e.getEnabled() == 1)
                .map(GlobalModelEntity::getModelName)
                .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    public Map<String, ModelInfo> getGlobalModelsFull() {
        List<GlobalModelEntity> all = globalModelRepository.findAll();
        if (all.isEmpty()) {
            return Collections.emptyMap();
        }
        Map<String, ModelInfo> result = new LinkedHashMap<>();
        for (GlobalModelEntity entity : all) {
            try {
                ModelInfo config = objectMapper.readValue(entity.getCustomConfig(), ModelInfo.class);
                if (config != null && config.getProvider() != null) {
                    if (entity.getEnabled() == 0) {
                        config.set_enabled(false);
                    }
                    result.put(entity.getModelName(), config);
                }
            } catch (Exception e) {
                log.debug("Failed to parse custom_config for model {}: {}", entity.getModelName(), e.getMessage());
            }
        }
        return result;
    }

    public List<Map<String, Object>> getGlobalModels() {
        List<GlobalModelEntity> all = globalModelRepository.findAll();
        if (all.isEmpty()) {
            List<Map<String, Object>> result = new ArrayList<>();
            for (Map.Entry<String, ModelInfo> entry : DEFAULT_MODELS.entrySet()) {
                Map<String, Object> map = objectMapper.convertValue(entry.getValue(), Map.class);
                map.put("model_name", entry.getKey());
                map.put("enabled", true);
                result.add(map);
            }
            return result;
        }

        List<Map<String, Object>> result = new ArrayList<>();
        for (GlobalModelEntity entity : all) {
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("model_name", entity.getModelName());
            entry.put("enabled", entity.getEnabled() == 1);
            entry.put("description", entity.getDescription());
            try {
                Map<String, Object> config = objectMapper.readValue(entity.getCustomConfig(), Map.class);
                entry.putAll(config);
            } catch (Exception e) {
                log.debug("Failed to parse custom_config for model {}", entity.getModelName());
            }
            result.add(entry);
        }
        return result;
    }

    @CacheEvict(value = "catalog", allEntries = true)
    @Transactional
    public void addGlobalModel(ModelCreate modelData) {
        String modelName = modelData.getModelName();
        String description = modelData.getDescription() != null ? modelData.getDescription() : "";

        Map<String, Object> configFields = new LinkedHashMap<>();
        configFields.put("provider", modelData.getProvider() != null ? modelData.getProvider() : "unknown");
        configFields.put("openrouter_id", modelData.getOpenrouterId() != null && !modelData.getOpenrouterId().isEmpty()
                ? modelData.getOpenrouterId() : modelName);
        configFields.put("tier", modelData.getTier() != null ? modelData.getTier() : "medium");
        configFields.put("cost_per_m_input", modelData.getCostPerMInput());
        configFields.put("cost_per_m_output", modelData.getCostPerMOutput());
        configFields.put("avg_latency_ms", modelData.getAvgLatencyMs());
        configFields.put("regions", modelData.getRegions() != null ? modelData.getRegions() : List.of("US"));
        configFields.put("max_context", modelData.getMaxContext());
        configFields.put("description", description);

        GlobalModelEntity entity = new GlobalModelEntity();
        entity.setModelName(modelName);
        entity.setEnabled(1);
        entity.setDescription(description);
        try {
            entity.setCustomConfig(objectMapper.writeValueAsString(configFields));
        } catch (Exception e) {
            entity.setCustomConfig("{}");
        }
        globalModelRepository.save(entity);
    }

    @CacheEvict(value = "catalog", allEntries = true)
    @Transactional
    public boolean removeGlobalModel(String modelName) {
        if (globalModelRepository.existsById(modelName)) {
            globalModelRepository.deleteById(modelName);
            return true;
        }
        return false;
    }

    @CacheEvict(value = "catalog", allEntries = true)
    @Transactional
    public void updateGlobalModel(String modelName, boolean enabled, String description) {
        GlobalModelEntity entity = globalModelRepository.findById(modelName).orElse(null);
        if (entity != null) {
            String customConfig = entity.getCustomConfig();
            if (description != null && !description.isEmpty()) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> config = objectMapper.readValue(customConfig, Map.class);
                    config.put("description", description);
                    customConfig = objectMapper.writeValueAsString(config);
                } catch (Exception e) {
                    log.debug("Failed to update description in custom_config");
                }
            }
            entity.setEnabled(enabled ? 1 : 0);
            entity.setDescription(description != null ? description : entity.getDescription());
            entity.setCustomConfig(customConfig);
            globalModelRepository.save(entity);
        } else {
            entity = new GlobalModelEntity();
            entity.setModelName(modelName);
            entity.setEnabled(enabled ? 1 : 0);
            entity.setDescription(description != null ? description : "");
            entity.setCustomConfig("{}");
            globalModelRepository.save(entity);
        }
    }

    @Transactional
    public void seedDefaultModels() {
        long count = globalModelRepository.count();
        if (count > 0) {
            return;
        }
        for (Map.Entry<String, ModelInfo> entry : DEFAULT_MODELS.entrySet()) {
            ModelInfo info = entry.getValue();
            ModelCreate modelData = new ModelCreate();
            modelData.setModelName(entry.getKey());
            modelData.setProvider(info.getProvider());
            modelData.setOpenrouterId(info.getOpenrouterId());
            modelData.setTier(info.getTier());
            modelData.setCostPerMInput(info.getCostPerMInput());
            modelData.setCostPerMOutput(info.getCostPerMOutput());
            modelData.setAvgLatencyMs(info.getAvgLatencyMs());
            modelData.setRegions(info.getRegions());
            modelData.setMaxContext(info.getMaxContext());
            modelData.setDescription(info.getDescription());
            addGlobalModel(modelData);
        }
    }
}
