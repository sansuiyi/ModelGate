package com.modelgate.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class OpenRouterModel {

    private String id;
    private String name;
    private int contextLength;
    private double costPerMInput;
    private double costPerMOutput;
    private String provider;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getContextLength() {
        return contextLength;
    }

    public void setContextLength(int contextLength) {
        this.contextLength = contextLength;
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

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }
}
