package com.modelgate.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI modelGateOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("ModelGate")
                        .description("Contract-Aware AI Control Plane")
                        .version("0.1.0"));
    }
}
