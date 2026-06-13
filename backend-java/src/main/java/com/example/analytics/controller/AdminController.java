package com.example.analytics.controller;

import com.example.analytics.model.User;
import com.example.analytics.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @Autowired
    private UserRepository userRepository;

    @GetMapping("/users")
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userRepository.findAll();
        // Clear passwords from response for security
        users.forEach(u -> u.setPassword(null));
        return ResponseEntity.ok(users);
    }

    @PostMapping("/users/{id}/role")
    public ResponseEntity<?> updateUserRole(@PathVariable Long id, @RequestBody Map<String, String> request) {
        String newRole = request.get("role");
        if (newRole == null || (!newRole.equals("USER") && !newRole.equals("PREMIUM_USER") && !newRole.equals("ADMIN"))) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "Invalid role specified.");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> userOpt = userRepository.findById(id);
        if (!userOpt.isPresent()) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "User not found.");
            return ResponseEntity.notFound().build();
        }

        User user = userOpt.get();
        user.setRole(newRole);
        userRepository.save(user);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "User role updated successfully.");
        response.put("userId", id);
        response.put("newRole", newRole);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/users/{id}/subscription")
    public ResponseEntity<?> updateUserSubscription(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        String newPlan = (String) request.get("subscriptionPlan");
        if (newPlan == null) {
            newPlan = (String) request.get("plan");
        }
        if (newPlan == null || (!newPlan.equals("FREE") && !newPlan.equals("STARTER") && !newPlan.equals("PROFESSIONAL") && !newPlan.equals("ENTERPRISE"))) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "Invalid subscription plan specified.");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> userOpt = userRepository.findById(id);
        if (!userOpt.isPresent()) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "User not found.");
            return ResponseEntity.notFound().build();
        }

        User user = userOpt.get();
        user.setSubscriptionPlan(newPlan);
        
        int durationMonths = 0;
        if (newPlan.equals("STARTER")) {
            durationMonths = 3;
        } else if (newPlan.equals("PROFESSIONAL")) {
            durationMonths = 6;
        } else if (newPlan.equals("ENTERPRISE")) {
            durationMonths = 12;
        }

        if (durationMonths > 0) {
            user.setSubscriptionExpiresAt(java.time.LocalDateTime.now().plusMonths(durationMonths));
            if ("USER".equalsIgnoreCase(user.getRole())) {
                user.setRole("PREMIUM_USER");
            }
        } else {
            user.setSubscriptionExpiresAt(null);
            if ("PREMIUM_USER".equalsIgnoreCase(user.getRole())) {
                user.setRole("USER");
            }
        }
        
        user.setDashboardsGeneratedThisMonth(0);
        user.setLimitResetAt(java.time.LocalDateTime.now().plusMonths(1));
        userRepository.save(user);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "User subscription updated successfully.");
        response.put("userId", id);
        response.put("subscriptionPlan", newPlan);
        response.put("role", user.getRole());
        return ResponseEntity.ok(response);
    }
}

