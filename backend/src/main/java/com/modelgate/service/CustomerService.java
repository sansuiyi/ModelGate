package com.modelgate.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.modelgate.common.ResourceNotFoundException;
import com.modelgate.domain.CustomerProfile;
import com.modelgate.dto.CustomerProfileUpdate;
import com.modelgate.entity.CustomerEntity;
import com.modelgate.repository.CustomerRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class CustomerService {

    private static final Logger log = LoggerFactory.getLogger(CustomerService.class);

    private final CustomerRepository customerRepository;
    private final ObjectMapper objectMapper;

    public CustomerService(CustomerRepository customerRepository, ObjectMapper objectMapper) {
        this.customerRepository = customerRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public void saveCustomer(CustomerProfile profile) {
        if (profile.getCreatedAt() == null || profile.getCreatedAt().isEmpty()) {
            profile.setCreatedAt(Instant.now().toString());
        }
        try {
            String json = objectMapper.writeValueAsString(profile);
            CustomerEntity entity = customerRepository.findById(profile.getCustomerId())
                    .orElseGet(CustomerEntity::new);
            entity.setCustomerId(profile.getCustomerId());
            entity.setData(json);
            entity.setCreatedAt(profile.getCreatedAt());
            customerRepository.save(entity);
        } catch (Exception e) {
            throw new RuntimeException("Failed to save customer profile", e);
        }
    }

    public CustomerProfile getCustomer(String customerId) {
        return customerRepository.findById(customerId)
                .map(this::deserialize)
                .orElse(null);
    }

    public CustomerProfile getCustomerOrThrow(String customerId) {
        CustomerProfile profile = getCustomer(customerId);
        if (profile == null) {
            throw new ResourceNotFoundException("Customer '" + customerId + "' not found");
        }
        return profile;
    }

    public List<CustomerProfile> listCustomers() {
        return customerRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(this::deserialize)
                .collect(Collectors.toList());
    }

    @Transactional
    public boolean deleteCustomer(String customerId) {
        if (customerRepository.existsById(customerId)) {
            customerRepository.deleteById(customerId);
            return true;
        }
        return false;
    }

    @Transactional
    public CustomerProfile updateCustomer(String customerId, CustomerProfileUpdate update) {
        CustomerProfile profile = getCustomerOrThrow(customerId);

        if (update.getObjective() != null) {
            profile.setObjective(update.getObjective());
        }
        if (update.getUseCase() != null) {
            profile.setUseCase(update.getUseCase());
        }
        if (update.getConstraints() != null) {
            profile.setConstraints(update.getConstraints());
        }
        if (update.getPerformance() != null) {
            profile.setPerformance(update.getPerformance());
        }
        if (update.getRoutingPreferences() != null) {
            profile.setRoutingPreferences(update.getRoutingPreferences());
        }
        if (update.getWarnings() != null) {
            profile.setWarnings(update.getWarnings());
        }

        saveCustomer(profile);
        return profile;
    }

    private CustomerProfile deserialize(CustomerEntity entity) {
        try {
            CustomerProfile profile = objectMapper.readValue(entity.getData(), CustomerProfile.class);
            profile.setCustomerId(entity.getCustomerId());
            profile.setCreatedAt(entity.getCreatedAt());
            return profile;
        } catch (Exception e) {
            log.error("Failed to deserialize customer {}: {}", entity.getCustomerId(), e.getMessage());
            throw new RuntimeException("Failed to deserialize customer profile", e);
        }
    }
}
