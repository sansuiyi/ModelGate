package com.modelgate.controller;

import com.modelgate.dto.CustomerStats;
import com.modelgate.dto.GlobalStats;
import com.modelgate.service.CustomerService;
import com.modelgate.service.StatsService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class LogController {

    private final StatsService statsService;
    private final CustomerService customerService;

    public LogController(StatsService statsService, CustomerService customerService) {
        this.statsService = statsService;
        this.customerService = customerService;
    }

    @GetMapping("/logs/{customerId}")
    public List<Map<String, Object>> getLogs(
            @PathVariable String customerId,
            @RequestParam(defaultValue = "100") int limit) {
        customerService.getCustomerOrThrow(customerId);
        return statsService.getRequestLogs(customerId, limit);
    }

    @GetMapping("/logs")
    public List<Map<String, Object>> getAllLogs(@RequestParam(defaultValue = "100") int limit) {
        return statsService.getRequestLogs(null, limit);
    }

    @GetMapping("/stats/{customerId}")
    public CustomerStats getStats(@PathVariable String customerId) {
        customerService.getCustomerOrThrow(customerId);
        return statsService.getCustomerStats(customerId);
    }

    @GetMapping("/stats")
    public GlobalStats getOverviewStats() {
        return statsService.getGlobalStats();
    }
}
