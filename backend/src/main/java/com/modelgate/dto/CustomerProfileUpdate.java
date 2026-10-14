package com.modelgate.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.modelgate.domain.CustomerConstraints;
import com.modelgate.domain.CustomerPerformance;

import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomerProfileUpdate {

    private String objective;
    private String useCase;
    private CustomerConstraints constraints;
    private CustomerPerformance performance;
    private Map<String, List<String>> routingPreferences;
    private List<Object> warnings;

    public String getObjective() {
        return objective;
    }

    public void setObjective(String objective) {
        this.objective = objective;
    }

    public String getUseCase() {
        return useCase;
    }

    public void setUseCase(String useCase) {
        this.useCase = useCase;
    }

    public CustomerConstraints getConstraints() {
        return constraints;
    }

    public void setConstraints(CustomerConstraints constraints) {
        this.constraints = constraints;
    }

    public CustomerPerformance getPerformance() {
        return performance;
    }

    public void setPerformance(CustomerPerformance performance) {
        this.performance = performance;
    }

    public Map<String, List<String>> getRoutingPreferences() {
        return routingPreferences;
    }

    public void setRoutingPreferences(Map<String, List<String>> routingPreferences) {
        this.routingPreferences = routingPreferences;
    }

    public List<Object> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<Object> warnings) {
        this.warnings = warnings;
    }
}
