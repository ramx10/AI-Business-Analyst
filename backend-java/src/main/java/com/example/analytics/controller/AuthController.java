package com.example.analytics.controller;

import com.example.analytics.model.User;
import com.example.analytics.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserRepository userRepository;

    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String password = request.get("password");
        String name = request.get("name");

        if (email == null || email.trim().isEmpty() || password == null || password.trim().isEmpty()) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "Email and password are required.");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> existingUser = userRepository.findByEmail(email);
        if (existingUser.isPresent()) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "An account with this email already exists.");
            return ResponseEntity.badRequest().body(response);
        }

        String googleId = "manual_" + UUID.randomUUID();
        String hashedPassword = passwordEncoder.encode(password);
        User user = new User(googleId, email, name != null ? name : "User", null, hashedPassword);
        userRepository.save(user);

        Map<String, String> response = new HashMap<>();
        response.put("message", "Registration successful!");
        response.put("token", user.getAuthToken());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String password = request.get("password");

        if (email == null || password == null) {
            Map<String, String> response = new HashMap<>();
            response.put("error", "Email and password are required.");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> userOpt = userRepository.findByEmail(email);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            if (passwordEncoder.matches(password, user.getPassword())) {
                Map<String, String> response = new HashMap<>();
                response.put("token", user.getAuthToken());
                response.put("name", user.getName());
                return ResponseEntity.ok(response);
            }
        }

        Map<String, String> response = new HashMap<>();
        response.put("error", "Invalid email or password.");
        return ResponseEntity.status(401).body(response);
    }
}
