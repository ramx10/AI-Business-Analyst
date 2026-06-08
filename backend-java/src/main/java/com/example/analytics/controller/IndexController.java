package com.example.analytics.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class IndexController {

    @GetMapping("/")
    public String index() {
        return "<html><body style='font-family: Arial, sans-serif; text-align: center; margin-top: 100px;'>"
                + "<h2>AI Business Analyst Backend is running!</h2>"
                + "<p>This is the Spring Boot API service.</p>"
                + "<p>To open the dashboard frontend app, please go to: "
                + "<a href='http://localhost:8000' style='color: #007bff; text-decoration: none; font-weight: bold;'>http://localhost:8000</a></p>"
                + "</body></html>";
    }
}
