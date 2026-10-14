package com.modelgate.controller;

import com.modelgate.domain.CustomerProfile;
import com.modelgate.dto.ExtractionRequest;
import com.modelgate.service.ContractExtractionService;
import com.modelgate.service.CustomerService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@RestController
public class ExtractionController {

    private final ContractExtractionService contractExtractionService;
    private final CustomerService customerService;

    public ExtractionController(ContractExtractionService contractExtractionService,
                                 CustomerService customerService) {
        this.contractExtractionService = contractExtractionService;
        this.customerService = customerService;
    }

    @PostMapping("/extract")
    public CustomerProfile extractFromJson(@RequestBody ExtractionRequest request) {
        CustomerProfile profile = contractExtractionService.extractProfile(
                request.getCustomerName(),
                request.getContractText(),
                request.getCustomInstructions()
        );
        customerService.saveCustomer(profile);
        return profile;
    }

    @PostMapping("/extract/upload")
    public CustomerProfile extractFromFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("customer_name") String customerName,
            @RequestParam(value = "custom_instructions", defaultValue = "") String customInstructions) {
        String contractText;
        try {
            contractText = new String(file.getBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new IllegalArgumentException("Could not read file. Please upload a text file.");
        }

        CustomerProfile profile = contractExtractionService.extractProfile(
                customerName,
                contractText,
                customInstructions
        );
        customerService.saveCustomer(profile);
        return profile;
    }
}
