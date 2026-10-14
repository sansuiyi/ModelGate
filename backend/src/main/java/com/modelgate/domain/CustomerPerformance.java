package com.modelgate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomerPerformance {

    private int latencyTargetMs = 3000;
    private String costSensitivity = "medium";

    public CustomerPerformance() {
    }

    public int getLatencyTargetMs() {
        return latencyTargetMs;
    }

    public void setLatencyTargetMs(int latencyTargetMs) {
        this.latencyTargetMs = latencyTargetMs;
    }

    public String getCostSensitivity() {
        return costSensitivity;
    }

    public void setCostSensitivity(String costSensitivity) {
        this.costSensitivity = costSensitivity;
    }
}
