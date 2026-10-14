package com.modelgate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.modelgate.util.SlugUtil;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomerProfile {

    private String customerId;
    private String customerName;
    private String useCase;
    private String objective;
    private CustomerConstraints constraints = new CustomerConstraints();
    private CustomerPerformance performance = new CustomerPerformance();
    private Map<String, List<String>> routingPreferences = new LinkedHashMap<>();
    private List<Object> warnings = new ArrayList<>();
    private String createdAt = "";

    public CustomerProfile() {
    }

    public void postLoad() {
        if (createdAt == null || createdAt.isEmpty()) {
            createdAt = Instant.now().toString();
        }
        if (customerId == null || customerId.isEmpty()) {
            customerId = SlugUtil.slugify(customerName);
        }
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public String getCustomerName() {
        return customerName;
    }

    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public String getUseCase() {
        return useCase;
    }

    public void setUseCase(String useCase) {
        this.useCase = useCase;
    }

    public String getObjective() {
        return objective;
    }

    public void setObjective(String objective) {
        this.objective = objective;
    }

    public CustomerConstraints getConstraints() {
        return constraints;
    }

    public void setConstraints(CustomerConstraints constraints) {
        this.constraints = constraints != null ? constraints : new CustomerConstraints();
    }

    public CustomerPerformance getPerformance() {
        return performance;
    }

    public void setPerformance(CustomerPerformance performance) {
        this.performance = performance != null ? performance : new CustomerPerformance();
    }

    public Map<String, List<String>> getRoutingPreferences() {
        return routingPreferences;
    }

    public void setRoutingPreferences(Map<String, List<String>> routingPreferences) {
        this.routingPreferences = routingPreferences != null ? routingPreferences : new LinkedHashMap<>();
    }

    public List<Object> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<Object> warnings) {
        this.warnings = warnings != null ? warnings : new ArrayList<>();
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}
