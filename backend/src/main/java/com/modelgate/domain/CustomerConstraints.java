package com.modelgate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CustomerConstraints {

    private String region = "any";
    private String privacyTier = "standard";
    private List<String> forbiddenProviders = new ArrayList<>();
    private List<String> allowedProviders = new ArrayList<>();

    public CustomerConstraints() {
    }

    public String getRegion() {
        return region;
    }

    public void setRegion(String region) {
        this.region = region;
    }

    public String getPrivacyTier() {
        return privacyTier;
    }

    public void setPrivacyTier(String privacyTier) {
        this.privacyTier = privacyTier;
    }

    public List<String> getForbiddenProviders() {
        return forbiddenProviders;
    }

    public void setForbiddenProviders(List<String> forbiddenProviders) {
        this.forbiddenProviders = forbiddenProviders != null ? forbiddenProviders : new ArrayList<>();
    }

    public List<String> getAllowedProviders() {
        return allowedProviders;
    }

    public void setAllowedProviders(List<String> allowedProviders) {
        this.allowedProviders = allowedProviders != null ? allowedProviders : new ArrayList<>();
    }
}
