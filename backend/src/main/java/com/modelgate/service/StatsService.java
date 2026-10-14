package com.modelgate.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.modelgate.domain.ModelInfo;
import com.modelgate.dto.CustomerStats;
import com.modelgate.dto.GlobalStats;
import com.modelgate.entity.RequestLogEntity;
import com.modelgate.repository.CustomerRepository;
import com.modelgate.repository.RequestLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class StatsService {

    private static final Logger log = LoggerFactory.getLogger(StatsService.class);

    private final RequestLogRepository requestLogRepository;
    private final CustomerRepository customerRepository;
    private final ModelCatalogService modelCatalogService;
    private final ObjectMapper objectMapper;

    public StatsService(RequestLogRepository requestLogRepository,
                        CustomerRepository customerRepository,
                        ModelCatalogService modelCatalogService,
                        ObjectMapper objectMapper) {
        this.requestLogRepository = requestLogRepository;
        this.customerRepository = customerRepository;
        this.modelCatalogService = modelCatalogService;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public void saveRequestLog(Map<String, Object> entry) {
        RequestLogEntity entity = new RequestLogEntity();
        entity.setCustomerId((String) entry.get("customer_id"));
        entity.setTimestamp((String) entry.get("timestamp"));
        entity.setPromptPreview((String) entry.getOrDefault("prompt_preview", ""));
        entity.setClassification((String) entry.getOrDefault("classification", ""));
        entity.setSelectedProvider((String) entry.getOrDefault("selected_provider", ""));
        entity.setSelectedModel((String) entry.getOrDefault("selected_model", ""));
        entity.setReason((String) entry.getOrDefault("reason", ""));
        entity.setLatencyMs(toInt(entry.get("latency_ms")));
        entity.setEstimatedCost(toDouble(entry.get("estimated_cost")));
        entity.setTokensUsed(toInt(entry.get("tokens_used")));
        entity.setInputTokens(toInt(entry.getOrDefault("input_tokens", 0)));
        entity.setOutputTokens(toInt(entry.getOrDefault("output_tokens", 0)));
        entity.setTtftMs(toInt(entry.getOrDefault("ttft_ms", 0)));
        entity.setStatus((String) entry.getOrDefault("status", "success"));
        try {
            entity.setCandidatesConsidered(objectMapper.writeValueAsString(entry.getOrDefault("candidates_considered", List.of())));
            entity.setCandidatesEliminated(objectMapper.writeValueAsString(entry.getOrDefault("candidates_eliminated", Map.of())));
        } catch (Exception e) {
            entity.setCandidatesConsidered("[]");
            entity.setCandidatesEliminated("{}");
        }
        requestLogRepository.save(entity);
    }

    public List<Map<String, Object>> getRequestLogs(String customerId, int limit) {
        List<RequestLogEntity> entities;
        int safeLimit = Math.max(1, limit);
        PageRequest pageRequest = PageRequest.of(0, safeLimit, Sort.by(Sort.Direction.DESC, "timestamp"));
        if (customerId != null && !customerId.isEmpty()) {
            entities = requestLogRepository.findByCustomerIdOrderByTimestampDesc(customerId, pageRequest);
        } else {
            entities = requestLogRepository.findAllByOrderByTimestampDesc(pageRequest);
        }

        List<Map<String, Object>> results = new ArrayList<>();
        for (RequestLogEntity entity : entities) {
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("id", entity.getId());
            d.put("customer_id", entity.getCustomerId());
            d.put("timestamp", entity.getTimestamp());
            d.put("prompt_preview", entity.getPromptPreview());
            d.put("classification", entity.getClassification());
            d.put("selected_provider", entity.getSelectedProvider());
            d.put("selected_model", entity.getSelectedModel());
            d.put("reason", entity.getReason());
            d.put("latency_ms", entity.getLatencyMs());
            d.put("estimated_cost", entity.getEstimatedCost());
            d.put("tokens_used", entity.getTokensUsed());
            d.put("input_tokens", entity.getInputTokens());
            d.put("output_tokens", entity.getOutputTokens());
            d.put("ttft_ms", entity.getTtftMs());
            d.put("status", entity.getStatus());
            d.put("candidates_considered", parseJson(entity.getCandidatesConsidered(), List.of()));
            d.put("candidates_eliminated", parseJson(entity.getCandidatesEliminated(), Map.of()));
            results.add(d);
        }
        return results;
    }

    public CustomerStats getCustomerStats(String customerId) {
        List<RequestLogEntity> rawRows = requestLogRepository.findByCustomerId(customerId);

        CustomerStats stats = new CustomerStats();
        if (rawRows.isEmpty()) {
            return stats;
        }

        int total = rawRows.size();
        List<Integer> latencies = rawRows.stream()
                .map(RequestLogEntity::getLatencyMs)
                .sorted()
                .collect(Collectors.toList());

        long totalLatency = rawRows.stream().mapToLong(RequestLogEntity::getLatencyMs).sum();
        double totalCost = rawRows.stream().mapToDouble(RequestLogEntity::getEstimatedCost).sum();
        int totalTokens = rawRows.stream().mapToInt(RequestLogEntity::getTokensUsed).sum();
        int totalInput = rawRows.stream().mapToInt(RequestLogEntity::getInputTokens).sum();
        int totalOutput = rawRows.stream().mapToInt(RequestLogEntity::getOutputTokens).sum();
        List<Integer> ttfts = rawRows.stream()
                .map(RequestLogEntity::getTtftMs)
                .filter(t -> t > 0)
                .collect(Collectors.toList());
        long successes = rawRows.stream()
                .filter(r -> "success".equals(r.getStatus() != null ? r.getStatus() : "success"))
                .count();

        Map<String, ModelInfo> catalog = modelCatalogService.getActiveCatalog();
        ModelInfo premiumInfo = findPremiumModel(catalog);
        double premiumTotal = computePremiumTotal(rawRows, premiumInfo);

        Map<String, Integer> modelDist = new LinkedHashMap<>();
        Map<String, Integer> tierDist = new LinkedHashMap<>();
        Map<String, Integer> providerDist = new LinkedHashMap<>();
        Map<String, Double> costByModel = new LinkedHashMap<>();
        Map<String, List<Integer>> latencyByModel = new LinkedHashMap<>();

        for (RequestLogEntity r : rawRows) {
            String model = r.getSelectedModel();
            String tier = r.getClassification();
            String provider = r.getSelectedProvider();
            modelDist.merge(model, 1, Integer::sum);
            tierDist.merge(tier, 1, Integer::sum);
            providerDist.merge(provider, 1, Integer::sum);
            costByModel.merge(model, r.getEstimatedCost(), (a, b) -> round6(a + b));
            latencyByModel.computeIfAbsent(model, k -> new ArrayList<>()).add(r.getLatencyMs());
        }

        Map<String, Double> avgLatencyByModel = new LinkedHashMap<>();
        for (Map.Entry<String, List<Integer>> entry : latencyByModel.entrySet()) {
            double avg = entry.getValue().stream().mapToInt(Integer::intValue).average().orElse(0);
            avgLatencyByModel.put(entry.getKey(), round1(avg));
        }

        List<Map<String, Object>> hourlyList = buildHourlyRequests(rawRows);

        int p95Idx = Math.min((int) (total * 0.95), total - 1);
        int p99Idx = Math.min((int) (total * 0.99), total - 1);

        stats.setTotalRequests(total);
        stats.setAvgLatencyMs(round1((double) totalLatency / total));
        stats.setP95LatencyMs(latencies.get(p95Idx));
        stats.setP99LatencyMs(latencies.get(p99Idx));
        stats.setTotalCost(round6(totalCost));
        stats.setCostSavingsVsPremium(round6(premiumTotal - totalCost));
        stats.setTotalTokens(totalTokens);
        stats.setTotalInputTokens(totalInput);
        stats.setTotalOutputTokens(totalOutput);
        stats.setAvgTtftMs(ttfts.isEmpty() ? 0 : round1(ttfts.stream().mapToInt(Integer::intValue).average().orElse(0)));
        stats.setSuccessRate(round1((double) successes / total * 100));
        stats.setModelDistribution(modelDist);
        stats.setRequestsByTier(tierDist);
        stats.setProviderDistribution(providerDist);
        stats.setCostByModel(costByModel);
        stats.setLatencyByModel(avgLatencyByModel);
        stats.setHourlyRequests(hourlyList);
        return stats;
    }

    public GlobalStats getGlobalStats() {
        List<RequestLogEntity> rawRows = requestLogRepository.findAllByOrderByTimestampDesc();
        long customerCount = customerRepository.count();

        GlobalStats stats = new GlobalStats();
        int total = rawRows.size();
        stats.setTotalCustomers((int) customerCount);

        if (total == 0) {
            return stats;
        }

        double totalCost = rawRows.stream().mapToDouble(RequestLogEntity::getEstimatedCost).sum();
        long totalLatency = rawRows.stream().mapToLong(RequestLogEntity::getLatencyMs).sum();

        Map<String, ModelInfo> catalog = modelCatalogService.getActiveCatalog();
        ModelInfo premiumInfo = findPremiumModel(catalog);
        double premiumTotal = computePremiumTotal(rawRows, premiumInfo);

        String today = Instant.now().atOffset(ZoneOffset.UTC).format(DateTimeFormatter.ISO_LOCAL_DATE);
        List<RequestLogEntity> todayRows = rawRows.stream()
                .filter(r -> r.getTimestamp() != null && r.getTimestamp().startsWith(today))
                .collect(Collectors.toList());

        Map<String, Integer> modelDist = new LinkedHashMap<>();
        Map<String, Integer> providerDist = new LinkedHashMap<>();
        Map<String, Integer> customerCounts = new LinkedHashMap<>();

        for (RequestLogEntity r : rawRows) {
            modelDist.merge(r.getSelectedModel(), 1, Integer::sum);
            providerDist.merge(r.getSelectedProvider(), 1, Integer::sum);
            customerCounts.merge(r.getCustomerId(), 1, Integer::sum);
        }

        List<Map<String, Object>> hourlyList = buildHourlyRequests(rawRows);

        stats.setTotalRequests(total);
        stats.setTotalCost(round6(totalCost));
        stats.setCostSavingsVsPremium(round6(premiumTotal - totalCost));
        stats.setAvgLatencyMs(round1((double) totalLatency / total));
        stats.setRequestsToday(todayRows.size());
        stats.setCostToday(round6(todayRows.stream().mapToDouble(RequestLogEntity::getEstimatedCost).sum()));
        stats.setModelDistribution(modelDist);
        stats.setProviderDistribution(providerDist);
        stats.setCustomerRequestCounts(customerCounts);
        stats.setHourlyRequests(hourlyList);
        return stats;
    }

    private ModelInfo findPremiumModel(Map<String, ModelInfo> catalog) {
        if (catalog == null || catalog.isEmpty()) {
            return new ModelInfo();
        }
        return catalog.values().stream()
                .max(Comparator.comparingDouble(m -> m.getCostPerMInput() + m.getCostPerMOutput()))
                .orElse(new ModelInfo());
    }

    private double computePremiumTotal(List<RequestLogEntity> rows, ModelInfo premiumInfo) {
        double total = 0;
        for (RequestLogEntity r : rows) {
            int inputTokens = r.getInputTokens() > 0 ? r.getInputTokens() : r.getTokensUsed() / 2;
            int outputTokens = r.getOutputTokens() > 0 ? r.getOutputTokens() : r.getTokensUsed() / 2;
            total += (inputTokens / 1_000_000.0) * premiumInfo.getCostPerMInput()
                    + (outputTokens / 1_000_000.0) * premiumInfo.getCostPerMOutput();
        }
        return total;
    }

    private List<Map<String, Object>> buildHourlyRequests(List<RequestLogEntity> rows) {
        Map<String, Integer> hourly = new TreeMap<>();
        DateTimeFormatter hourFmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:00").withZone(ZoneOffset.UTC);
        for (RequestLogEntity r : rows) {
            try {
                Instant ts = Instant.parse(r.getTimestamp());
                String hourKey = hourFmt.format(ts);
                hourly.merge(hourKey, 1, Integer::sum);
            } catch (DateTimeParseException e) {
                // skip unparseable timestamps
            }
        }
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : hourly.entrySet()) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("hour", entry.getKey());
            item.put("count", entry.getValue());
            result.add(item);
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private Object parseJson(String json, Object fallback) {
        if (json == null || json.isBlank()) {
            return fallback;
        }
        try {
            return objectMapper.readValue(json, Object.class);
        } catch (Exception e) {
            return fallback;
        }
    }

    private int toInt(Object value) {
        if (value instanceof Number n) {
            return n.intValue();
        }
        return 0;
    }

    private double toDouble(Object value) {
        if (value instanceof Number n) {
            return n.doubleValue();
        }
        return 0.0;
    }

    private double round6(double value) {
        return BigDecimal.valueOf(value).setScale(6, RoundingMode.HALF_UP).doubleValue();
    }

    private double round1(double value) {
        return BigDecimal.valueOf(value).setScale(1, RoundingMode.HALF_UP).doubleValue();
    }
}
