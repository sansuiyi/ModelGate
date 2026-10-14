package com.modelgate.controller;

import com.modelgate.dto.ChatCompletionRequest;
import com.modelgate.service.ProxyService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class ProxyController {

    private final ProxyService proxyService;

    public ProxyController(ProxyService proxyService) {
        this.proxyService = proxyService;
    }

    @GetMapping("/{customerId}/v1/models")
    public Map<String, Object> listModels(@PathVariable String customerId) {
        return proxyService.listModels(customerId);
    }

    @PostMapping("/{customerId}/v1/chat/completions")
    public ResponseEntity<Object> chatCompletions(
            @PathVariable String customerId,
            @RequestBody ChatCompletionRequest request) {
        ProxyService.ProxyResult result = proxyService.chatCompletions(customerId, request);

        HttpHeaders headers = new HttpHeaders();
        for (Map.Entry<String, String> entry : result.getHeaders().entrySet()) {
            headers.add(entry.getKey(), entry.getValue());
        }

        return ResponseEntity.ok()
                .headers(headers)
                .body(result.getBody());
    }
}
