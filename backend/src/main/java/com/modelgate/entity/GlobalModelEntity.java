package com.modelgate.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "global_models")
public class GlobalModelEntity {

    @Id
    @Column(name = "model_name")
    private String modelName;

    @Column(name = "enabled")
    private int enabled = 1;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description = "";

    @Column(name = "custom_config", columnDefinition = "TEXT")
    private String customConfig = "{}";

    public GlobalModelEntity() {
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public int getEnabled() {
        return enabled;
    }

    public void setEnabled(int enabled) {
        this.enabled = enabled;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCustomConfig() {
        return customConfig;
    }

    public void setCustomConfig(String customConfig) {
        this.customConfig = customConfig;
    }
}
