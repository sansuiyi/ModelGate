package com.modelgate.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "modelgate.classifier")
public class ClassifierProperties {

    private String ggufPath = "";
    private int nCtx = 512;
    private int nGpuLayers = -1;

    public String getGgufPath() {
        return ggufPath;
    }

    public void setGgufPath(String ggufPath) {
        this.ggufPath = ggufPath;
    }

    public int getNCtx() {
        return nCtx;
    }

    public void setNCtx(int nCtx) {
        this.nCtx = nCtx;
    }

    public int getNGpuLayers() {
        return nGpuLayers;
    }

    public void setNGpuLayers(int nGpuLayers) {
        this.nGpuLayers = nGpuLayers;
    }
}
