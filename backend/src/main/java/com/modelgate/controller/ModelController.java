package com.modelgate.controller;

import com.modelgate.dto.ModelCreate;
import com.modelgate.dto.ModelUpdate;
import com.modelgate.dto.OpenRouterModel;
import com.modelgate.service.ModelCatalogService;
import com.modelgate.service.OpenRouterService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/models")
public class ModelController {

    private final ModelCatalogService modelCatalogService;
    private final OpenRouterService openRouterService;

    public ModelController(ModelCatalogService modelCatalogService, OpenRouterService openRouterService) {
        this.modelCatalogService = modelCatalogService;
        this.openRouterService = openRouterService;
    }

    @GetMapping
    public List<Map<String, Object>> listModels() {
        return modelCatalogService.getGlobalModels();
    }

    @PostMapping
    public Map<String, String> createModel(@RequestBody ModelCreate model) {
        if (model.getOpenrouterId() == null || model.getOpenrouterId().isEmpty()) {
            model.setOpenrouterId(model.getModelName());
        }
        modelCatalogService.addGlobalModel(model);
        return Map.of("status", "created", "model_name", model.getModelName());
    }

    @DeleteMapping("/{modelName}")
    public ResponseEntity<Map<String, String>> deleteModel(@PathVariable String modelName) {
        if (!modelCatalogService.removeGlobalModel(modelName)) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(Map.of("status", "deleted", "model_name", modelName));
    }

    @PutMapping("/{modelName}")
    public Map<String, Object> toggleModel(
            @PathVariable String modelName,
            @RequestBody ModelUpdate update) {
        modelCatalogService.updateGlobalModel(modelName, update.isEnabled(), update.getDescription());
        return Map.of("status", "updated", "model_name", modelName, "enabled", update.isEnabled());
    }

    @GetMapping("/openrouter/catalog")
    public List<OpenRouterModel> openrouterCatalog(@RequestParam(defaultValue = "") String q) {
        return openRouterService.browseCatalog(q);
    }
}
