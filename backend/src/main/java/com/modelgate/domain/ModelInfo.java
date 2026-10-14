package com.modelgate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.ArrayList;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class ModelInfo {

    private String provider;
    private String openrouterId;
    private String tier;
    private double costPerMInput;
    private double costPerMOutput;
    private int avgLatencyMs;
    private List<String> regions = new ArrayList<>();
    private int maxContext;
    private String description;
    private Boolean _enabled;

    public ModelInfo() {
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public String getOpenrouterId() {
        return openrouterId;
    }

    public void setOpenrouterId(String openrouterId) {
        this.openrouterId = openrouterId;
    }

    public String getTier() {
        return tier;
    }

    public void setTier(String tier) {
        this.tier = tier;
    }

    public double getCostPerMInput() {
        return costPerMInput;
    }

    public void setCostPerMInput(double costPerMInput) {
        this.costPerMInput = costPerMInput;
    }

    public double getCostPerMOutput() {
        return costPerMOutput;
    }

    public void setCostPerMOutput(double costPerMOutput) {
        this.costPerMOutput = costPerMOutput;
    }

    public int getAvgLatencyMs() {
        return avgLatencyMs;
    }

    public void setAvgLatencyMs(int avgLatencyMs) {
        this.avgLatencyMs = avgLatencyMs;
    }

    public List<String> getRegions() {
        return regions;
    }

    public void setRegions(List<String> regions) {
        this.regions = regions != null ? regions : new ArrayList<>();
    }

    public int getMaxContext() {
        return maxContext;
    }

    public void setMaxContext(int maxContext) {
        this.maxContext = maxContext;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean get_enabled() {
        return _enabled;
    }

    public void set_enabled(Boolean _enabled) {
        this._enabled = _enabled;
    }
}
