package com.example.analytics;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

@SpringBootApplication
public class AnalyticsApplication {
    public static void main(String[] args) {
        loadEnv();
        SpringApplication.run(AnalyticsApplication.class, args);
    }

    @org.springframework.context.annotation.Bean
    public org.springframework.boot.CommandLineRunner initAdmin(
            com.example.analytics.repository.UserRepository userRepository) {
        return args -> {
            String adminEmail = "admin@example.com";
            if (!userRepository.findByEmail(adminEmail).isPresent()) {
                org.springframework.security.crypto.password.PasswordEncoder encoder = 
                    new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder();
                String hashedPassword = encoder.encode("admin123");
                String googleId = "manual_admin";
                com.example.analytics.model.User admin = new com.example.analytics.model.User(
                    googleId, adminEmail, "System Administrator", null, hashedPassword
                );
                admin.setRole("ADMIN");
                userRepository.save(admin);
                System.out.println("Auto-seeded admin user: " + adminEmail);
            }
        };
    }

    private static void loadEnv() {
        Path envPath = Paths.get(".env");
        if (!Files.exists(envPath)) {
            envPath = Paths.get("../.env");
        }
        if (Files.exists(envPath)) {
            try {
                List<String> lines = Files.readAllLines(envPath);
                for (String line : lines) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) {
                        continue;
                    }
                    int eqIdx = line.indexOf('=');
                    if (eqIdx > 0) {
                        String key = line.substring(0, eqIdx).trim();
                        String value = line.substring(eqIdx + 1).trim();
                        // Remove surrounding quotes if any
                        if (value.startsWith("\"") && value.endsWith("\"") && value.length() >= 2) {
                            value = value.substring(1, value.length() - 1);
                        } else if (value.startsWith("'") && value.endsWith("'") && value.length() >= 2) {
                            value = value.substring(1, value.length() - 1);
                        }
                        if (System.getProperty(key) == null && System.getenv(key) == null) {
                            System.setProperty(key, value);
                        }
                    }
                }
            } catch (IOException e) {
                System.err.println("Failed to load .env file: " + e.getMessage());
            }
        }
    }
}
