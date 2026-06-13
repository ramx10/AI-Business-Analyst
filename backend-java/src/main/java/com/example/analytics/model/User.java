package com.example.analytics.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "google_id", unique = true, nullable = false)
    private String googleId;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    private String name;
    
    @Column(name = "picture_url")
    private String pictureUrl;
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    private String password;

    @Column(name = "auth_token", unique = true)
    private String authToken;

    @Column(name = "role")
    private String role = "USER";

    @Column(name = "subscription_plan")
    private String subscriptionPlan = "FREE";

    @Column(name = "subscription_expires_at")
    private LocalDateTime subscriptionExpiresAt;

    @Column(name = "dashboards_generated_this_month")
    private Integer dashboardsGeneratedThisMonth = 0;

    @Column(name = "limit_reset_at")
    private LocalDateTime limitResetAt = LocalDateTime.now().plusMonths(1);

    // Constructors
    public User() {}

    public User(String googleId, String email, String name, String pictureUrl) {
        this.googleId = googleId;
        this.email = email;
        this.name = name;
        this.pictureUrl = pictureUrl;
        this.authToken = java.util.UUID.randomUUID().toString();
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    public User(String googleId, String email, String name, String pictureUrl, String password) {
        this.googleId = googleId;
        this.email = email;
        this.name = name;
        this.pictureUrl = pictureUrl;
        this.password = password;
        this.authToken = java.util.UUID.randomUUID().toString();
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    // Quota and Subscription status helpers
    public void checkSubscriptionStatus() {
        if (subscriptionPlan != null && !"FREE".equalsIgnoreCase(subscriptionPlan)) {
            if (subscriptionExpiresAt != null && LocalDateTime.now().isAfter(subscriptionExpiresAt)) {
                this.subscriptionPlan = "FREE";
                this.subscriptionExpiresAt = null;
                if (!"ADMIN".equalsIgnoreCase(this.role)) {
                    this.role = "USER";
                }
            }
        }
    }

    public boolean checkAndResetLimits() {
        LocalDateTime now = LocalDateTime.now();
        if (limitResetAt == null || now.isAfter(limitResetAt)) {
            this.dashboardsGeneratedThisMonth = 0;
            this.limitResetAt = now.plusMonths(1);
            return true;
        }
        return false;
    }

    public int getDashboardLimit() {
        checkSubscriptionStatus();
        if ("STARTER".equalsIgnoreCase(subscriptionPlan)) {
            return 50;
        } else if ("PROFESSIONAL".equalsIgnoreCase(subscriptionPlan)) {
            return 200;
        } else if ("ENTERPRISE".equalsIgnoreCase(subscriptionPlan)) {
            return Integer.MAX_VALUE;
        } else {
            return 5;
        }
    }

    public boolean incrementGeneration() {
        checkSubscriptionStatus();
        checkAndResetLimits();
        if (this.dashboardsGeneratedThisMonth == null) {
            this.dashboardsGeneratedThisMonth = 0;
        }
        if (this.dashboardsGeneratedThisMonth >= getDashboardLimit()) {
            return false;
        }
        this.dashboardsGeneratedThisMonth++;
        return true;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getGoogleId() { return googleId; }
    public void setGoogleId(String googleId) { this.googleId = googleId; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getPictureUrl() { return pictureUrl; }
    public void setPictureUrl(String pictureUrl) { this.pictureUrl = pictureUrl; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getAuthToken() { return authToken; }
    public void setAuthToken(String authToken) { this.authToken = authToken; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public String getRole() { return role != null ? role : "USER"; }
    public void setRole(String role) { this.role = role; }

    public String getSubscriptionPlan() { return subscriptionPlan != null ? subscriptionPlan : "FREE"; }
    public void setSubscriptionPlan(String subscriptionPlan) { this.subscriptionPlan = subscriptionPlan; }

    public LocalDateTime getSubscriptionExpiresAt() { return subscriptionExpiresAt; }
    public void setSubscriptionExpiresAt(LocalDateTime subscriptionExpiresAt) { this.subscriptionExpiresAt = subscriptionExpiresAt; }

    public int getDashboardsGeneratedThisMonth() { return dashboardsGeneratedThisMonth != null ? dashboardsGeneratedThisMonth : 0; }
    public void setDashboardsGeneratedThisMonth(Integer dashboardsGeneratedThisMonth) { this.dashboardsGeneratedThisMonth = dashboardsGeneratedThisMonth; }

    public LocalDateTime getLimitResetAt() { return limitResetAt; }
    public void setLimitResetAt(LocalDateTime limitResetAt) { this.limitResetAt = limitResetAt; }
}

