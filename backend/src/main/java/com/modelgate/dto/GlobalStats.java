package com.modelgate.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class GlobalStats {

    private int totalRequests;
    private int totalCustomers;
    private double totalCost;
    private double costSavingsVsPremium;
    private double avgLatencyMs;
    private int requestsToday;
    private double costToday;
    private Map<String, Integer> modelDistribution = new LinkedHashMap<>();
    private Map<String, Integer> providerDistribution = new LinkedHashMap<>();
    private Map<String, Integer> customerRequestCounts = new LinkedHashMap<>();
    private List<Map<String, Object>> hourlyRequests = new java.util.ArrayList<>();

    public int getTotalRequests() {
        return totalRequests;
    }

    public void setTotalRequests(int totalRequests) {
        this.totalRequests = totalRequests;
    }

    public int getTotalCustomers() {
        return totalCustomers;
    }

    public void setTotalCustomers(int totalCustomers) {
        this.totalCustomers = totalCustomers;
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

    public double getAvgLatencyMs() {
        return avgLatencyMs;
    }

    public void setAvgLatencyMs(double avgLatencyMs) {
        this.avgLatencyMs = avgLatencyMs;
    }

    public int getRequestsToday() {
        return requestsToday;
    }

    public void setRequestsToday(int requestsToday) {
        this.requestsToday = requestsToday;
    }

    public double getCostToday() {
        return costToday;
    }

    public void setCostToday(double costToday) {
        this.costToday = costToday;
    }

    public Map<String, Integer> getModelDistribution() {
        return modelDistribution;
    }

    public void setModelDistribution(Map<String, Integer> modelDistribution) {
        this.modelDistribution = modelDistribution;
    }

    public Map<String, Integer> getProviderDistribution() {
        return providerDistribution;
    }

    public void setProviderDistribution(Map<String, Integer> providerDistribution) {
        this.providerDistribution = providerDistribution;
    }

    public Map<String, Integer> getCustomerRequestCounts() {
        return customerRequestCounts;
    }

    public void setCustomerRequestCounts(Map<String, Integer> customerRequestCounts) {
        this.customerRequestCounts = customerRequestCounts;
    }

    public List<Map<String, Object>> getHourlyRequests() {
        return hourlyRequests;
    }

    public void setHourlyRequests(List<Map<String, Object>> hourlyRequests) {
        this.hourlyRequests = hourlyRequests;
    }
}
