package com.modelgate.controller;

import com.modelgate.domain.CustomerProfile;
import com.modelgate.dto.CustomerProfileUpdate;
import com.modelgate.service.CustomerService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/customers")
public class CustomerController {

    private final CustomerService customerService;

    public CustomerController(CustomerService customerService) {
        this.customerService = customerService;
    }

    @GetMapping
    public List<CustomerProfile> getCustomers() {
        return customerService.listCustomers();
    }

    @GetMapping("/{customerId}")
    public CustomerProfile getCustomerById(@PathVariable String customerId) {
        return customerService.getCustomerOrThrow(customerId);
    }

    @PostMapping
    public CustomerProfile createCustomer(@RequestBody CustomerProfile profile) {
        if (profile.getCustomerId() == null || profile.getCustomerId().isEmpty()) {
            profile.postLoad();
        }
        customerService.saveCustomer(profile);
        return profile;
    }

    @PutMapping("/{customerId}")
    public CustomerProfile updateCustomer(
            @PathVariable String customerId,
            @RequestBody CustomerProfileUpdate update) {
        return customerService.updateCustomer(customerId, update);
    }

    @DeleteMapping("/{customerId}")
    public ResponseEntity<Map<String, String>> removeCustomer(@PathVariable String customerId) {
        if (!customerService.deleteCustomer(customerId)) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(Map.of("status", "deleted", "customer_id", customerId));
    }
}
