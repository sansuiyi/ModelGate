package com.modelgate.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.List;

@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");
        config.setAllowCredentials(true);
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setExposedHeaders(List.of(
                "X-Routing-Decision",
                "X-Model-Used",
                "X-Classification",
                "X-Latency-Ms",
                "X-TTFT-Ms",
                "X-Classify-Ms",
                "X-Cost"
        ));
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
