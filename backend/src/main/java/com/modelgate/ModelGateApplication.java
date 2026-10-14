package com.modelgate;

import com.modelgate.service.ModelCatalogService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@EnableCaching
public class ModelGateApplication {

    public static void main(String[] args) {
        SpringApplication.run(ModelGateApplication.class, args);
    }

    @Bean
    CommandLineRunner initDatabase(ModelCatalogService modelCatalogService) {
        return args -> modelCatalogService.seedDefaultModels();
    }
}
