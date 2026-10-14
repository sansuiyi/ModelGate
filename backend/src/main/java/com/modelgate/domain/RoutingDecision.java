package com.modelgate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class RoutingDecision {

    private String selectedProvider;
    private String selectedModel;
    private String classification;
    private String reason;
    private List<String> candidatesConsidered = new ArrayList<>();
    private Map<String, String> candidatesEliminated = new LinkedHashMap<>();

    public RoutingDecision() {
    }

    public String getSelectedProvider() {
        return selectedProvider;
    }

    public void setSelectedProvider(String selectedProvider) {
        this.selectedProvider = selectedProvider;
    }

    public String getSelectedModel() {
        return selectedModel;
    }

    public void setSelectedModel(String selectedModel) {
        this.selectedModel = selectedModel;
    }

    public String getClassification() {
        return classification;
    }

    public void setClassification(String classification) {
        this.classification = classification;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public List<String> getCandidatesConsidered() {
        return candidatesConsidered;
    }

    public void setCandidatesConsidered(List<String> candidatesConsidered) {
        this.candidatesConsidered = candidatesConsidered != null ? candidatesConsidered : new ArrayList<>();
    }

    public Map<String, String> getCandidatesEliminated() {
        return candidatesEliminated;
    }

    public void setCandidatesEliminated(Map<String, String> candidatesEliminated) {
        this.candidatesEliminated = candidatesEliminated != null ? candidatesEliminated : new LinkedHashMap<>();
    }
}
