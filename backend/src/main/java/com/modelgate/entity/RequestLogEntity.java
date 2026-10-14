package com.modelgate.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "request_logs")
public class RequestLogEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private String customerId;

    @Column(name = "timestamp", nullable = false)
    private String timestamp;

    @Column(name = "prompt_preview", columnDefinition = "TEXT")
    private String promptPreview;

    @Column(name = "classification")
    private String classification;

    @Column(name = "selected_provider")
    private String selectedProvider;

    @Column(name = "selected_model")
    private String selectedModel;

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;

    @Column(name = "latency_ms")
    private int latencyMs;

    @Column(name = "estimated_cost")
    private double estimatedCost;

    @Column(name = "tokens_used")
    private int tokensUsed = 0;

    @Column(name = "input_tokens")
    private int inputTokens = 0;

    @Column(name = "output_tokens")
    private int outputTokens = 0;

    @Column(name = "ttft_ms")
    private int ttftMs = 0;

    @Column(name = "status")
    private String status = "success";

    @Column(name = "candidates_considered", columnDefinition = "TEXT")
    private String candidatesConsidered = "[]";

    @Column(name = "candidates_eliminated", columnDefinition = "TEXT")
    private String candidatesEliminated = "{}";

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getPromptPreview() {
        return promptPreview;
    }

    public void setPromptPreview(String promptPreview) {
        this.promptPreview = promptPreview;
    }

    public String getClassification() {
        return classification;
    }

    public void setClassification(String classification) {
        this.classification = classification;
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

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public int getLatencyMs() {
        return latencyMs;
    }

    public void setLatencyMs(int latencyMs) {
        this.latencyMs = latencyMs;
    }

    public double getEstimatedCost() {
        return estimatedCost;
    }

    public void setEstimatedCost(double estimatedCost) {
        this.estimatedCost = estimatedCost;
    }

    public int getTokensUsed() {
        return tokensUsed;
    }

    public void setTokensUsed(int tokensUsed) {
        this.tokensUsed = tokensUsed;
    }

    public int getInputTokens() {
        return inputTokens;
    }

    public void setInputTokens(int inputTokens) {
        this.inputTokens = inputTokens;
    }

    public int getOutputTokens() {
        return outputTokens;
    }

    public void setOutputTokens(int outputTokens) {
        this.outputTokens = outputTokens;
    }

    public int getTtftMs() {
        return ttftMs;
    }

    public void setTtftMs(int ttftMs) {
        this.ttftMs = ttftMs;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCandidatesConsidered() {
        return candidatesConsidered;
    }

    public void setCandidatesConsidered(String candidatesConsidered) {
        this.candidatesConsidered = candidatesConsidered;
    }

    public String getCandidatesEliminated() {
        return candidatesEliminated;
    }

    public void setCandidatesEliminated(String candidatesEliminated) {
        this.candidatesEliminated = candidatesEliminated;
    }
}
