package com.modelgate.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ModelCreate {

    private String modelName;
    private String provider;
    private String openrouterId = "";
    private String tier = "medium";
    private double costPerMInput = 1.0;
    private double costPerMOutput = 5.0;
    private int avgLatencyMs = 500;
    private List<String> regions = new ArrayList<>(List.of("US"));
    private int maxContext = 128000;
    private String description = "";

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
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
        this.regions = regions;
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
}
