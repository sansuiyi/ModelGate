package com.modelgate.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "modelgate.data")
public class DataProperties {

    private String fallbackProfilesDir = "./backend/data/fallback_profiles";

    public String getFallbackProfilesDir() {
        return fallbackProfilesDir;
    }

    public void setFallbackProfilesDir(String fallbackProfilesDir) {
        this.fallbackProfilesDir = fallbackProfilesDir;
    }
}
