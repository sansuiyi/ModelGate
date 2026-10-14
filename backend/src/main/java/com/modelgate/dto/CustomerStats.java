package com.modelgate.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomerStats {

    private int totalRequests;
    private double avgLatencyMs;
    private double p95LatencyMs = 0.0;
    private double p99LatencyMs = 0.0;
    private double totalCost;
    private double costSavingsVsPremium;
    private int totalTokens = 0;
    private int totalInputTokens = 0;
    private int totalOutputTokens = 0;
    private double avgTtftMs = 0.0;
    private double successRate = 100.0;
    private Map<String, Integer> modelDistribution = new LinkedHashMap<>();
    private Map<String, Integer> requestsByTier = new LinkedHashMap<>();
    private Map<String, Integer> providerDistribution = new LinkedHashMap<>();
    private Map<String, Double> costByModel = new LinkedHashMap<>();
    private Map<String, Double> latencyByModel = new LinkedHashMap<>();
    private List<Map<String, Object>> hourlyRequests = new java.util.ArrayList<>();

    public int getTotalRequests() {
        return totalRequests;
    }

    public void setTotalRequests(int totalRequests) {
        this.totalRequests = totalRequests;
    }

    public double getAvgLatencyMs() {
        return avgLatencyMs;
    }

    public void setAvgLatencyMs(double avgLatencyMs) {
        this.avgLatencyMs = avgLatencyMs;
    }

    public double getP95LatencyMs() {
        return p95LatencyMs;
    }

    public void setP95LatencyMs(double p95LatencyMs) {
        this.p95LatencyMs = p95LatencyMs;
    }

    public double getP99LatencyMs() {
        return p99LatencyMs;
    }

    public void setP99LatencyMs(double p99LatencyMs) {
        this.p99LatencyMs = p99LatencyMs;
    }

    public double getTotalCost() {
        return totalCost;
    }

    public void setTotalCost(double totalCost) {
        this.totalCost = totalCost;
    }

    public double getCostSavingsVsPremium() {
        return costSavingsVsPremium;
    }

    public void setCostSavingsVsPremium(double costSavingsVsPremium) {
        this.costSavingsVsPremium = costSavingsVsPremium;
    }

    public int getTotalTokens() {
        return totalTokens;
    }

    public void setTotalTokens(int totalTokens) {
        this.totalTokens = totalTokens;
    }

    public int getTotalInputTokens() {
        return totalInputTokens;
    }

    public void setTotalInputTokens(int totalInputTokens) {
        this.totalInputTokens = totalInputTokens;
    }

    public int getTotalOutputTokens() {
        return totalOutputTokens;
    }

    public void setTotalOutputTokens(int totalOutputTokens) {
        this.totalOutputTokens = totalOutputTokens;
    }

    public double getAvgTtftMs() {
        return avgTtftMs;
    }

    public void setAvgTtftMs(double avgTtftMs) {
        this.avgTtftMs = avgTtftMs;
    }

    public double getSuccessRate() {
        return successRate;
    }

    public void setSuccessRate(double successRate) {
        this.successRate = successRate;
    }

    public Map<String, Integer> getModelDistribution() {
        return modelDistribution;
    }

    public void setModelDistribution(Map<String, Integer> modelDistribution) {
        this.modelDistribution = modelDistribution;
    }

    public Map<String, Integer> getRequestsByTier() {
        return requestsByTier;
    }

    public void setRequestsByTier(Map<String, Integer> requestsByTier) {
        this.requestsByTier = requestsByTier;
    }

    public Map<String, Integer> getProviderDistribution() {
        return providerDistribution;
    }

    public void setProviderDistribution(Map<String, Integer> providerDistribution) {
        this.providerDistribution = providerDistribution;
    }

    public Map<String, Double> getCostByModel() {
        return costByModel;
    }

    public void setCostByModel(Map<String, Double> costByModel) {
        this.costByModel = costByModel;
    }

    public Map<String, Double> getLatencyByModel() {
        return latencyByModel;
    }

    public void setLatencyByModel(Map<String, Double> latencyByModel) {
        this.latencyByModel = latencyByModel;
    }

    public List<Map<String, Object>> getHourlyRequests() {
        return hourlyRequests;
    }

    public void setHourlyRequests(List<Map<String, Object>> hourlyRequests) {
        this.hourlyRequests = hourlyRequests;
    }
}
