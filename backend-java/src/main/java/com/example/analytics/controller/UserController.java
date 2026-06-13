package com.example.analytics.controller;

import com.example.analytics.model.User;
import com.example.analytics.model.DashboardHistory;
import com.example.analytics.repository.UserRepository;
import com.example.analytics.repository.DashboardHistoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DashboardHistoryRepository dashboardHistoryRepository;

    @Autowired
    private com.example.analytics.config.JwtUtil jwtUtil;

    @Autowired
    private com.example.analytics.service.PaymentGatewayService paymentGatewayService;

    @PostMapping("/upgrade")
    public ResponseEntity<?> upgradeToPremium() {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (!(principal instanceof User)) {
            return ResponseEntity.status(401).build();
        }
        User user = (User) principal;
        
        java.util.Optional<User> userOpt = userRepository.findById(user.getId());
        if (!userOpt.isPresent()) {
            return ResponseEntity.status(404).build();
        }
        
        User dbUser = userOpt.get();
        dbUser.setRole("PREMIUM_USER");
        dbUser.setSubscriptionPlan("STARTER");
        dbUser.setSubscriptionExpiresAt(java.time.LocalDateTime.now().plusMonths(3));
        userRepository.save(dbUser);
        
        String token = jwtUtil.generateToken(dbUser.getEmail(), dbUser.getRole(), dbUser.getId());
        
        Map<String, String> response = new java.util.HashMap<>();
        response.put("message", "Upgraded to Premium plan successfully!");
        response.put("token", token);
        response.put("role", dbUser.getRole());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/subscribe")
    public ResponseEntity<?> subscribe(@RequestBody Map<String, String> request) {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (!(principal instanceof User)) {
            return ResponseEntity.status(401).build();
        }
        User user = (User) principal;
        
        String plan = request.get("plan");
        String paymentMethod = request.get("paymentMethod");
        String paymentToken = request.get("paymentToken");

        if (plan == null || (!plan.equals("FREE") && !plan.equals("STARTER") && !plan.equals("PROFESSIONAL") && !plan.equals("ENTERPRISE"))) {
            Map<String, String> response = new java.util.HashMap<>();
            response.put("error", "Invalid subscription plan specified.");
            return ResponseEntity.badRequest().body(response);
        }

        java.util.Optional<User> userOpt = userRepository.findById(user.getId());
        if (!userOpt.isPresent()) {
            return ResponseEntity.status(404).build();
        }
        User dbUser = userOpt.get();

        double price = 0.0;
        int durationMonths = 0;
        if (plan.equals("STARTER")) {
            price = 27.0;
            durationMonths = 3;
        } else if (plan.equals("PROFESSIONAL")) {
            price = 42.0;
            durationMonths = 6;
        } else if (plan.equals("ENTERPRISE")) {
            price = 60.0;
            durationMonths = 12;
        }

        if (price > 0) {
            com.example.analytics.service.PaymentGatewayService.PaymentResult paymentResult = 
                paymentGatewayService.processPayment(plan, price, paymentMethod != null ? paymentMethod : "stripe", paymentToken != null ? paymentToken : "tok_visa");
            
            if (!paymentResult.isSuccess()) {
                Map<String, String> response = new java.util.HashMap<>();
                response.put("error", paymentResult.getErrorMessage());
                return ResponseEntity.badRequest().body(response);
            }
        }

        dbUser.setSubscriptionPlan(plan);
        if (durationMonths > 0) {
            dbUser.setSubscriptionExpiresAt(java.time.LocalDateTime.now().plusMonths(durationMonths));
            if ("USER".equalsIgnoreCase(dbUser.getRole())) {
                dbUser.setRole("PREMIUM_USER");
            }
        } else {
            dbUser.setSubscriptionExpiresAt(null);
            if ("PREMIUM_USER".equalsIgnoreCase(dbUser.getRole())) {
                dbUser.setRole("USER");
            }
        }
        dbUser.setDashboardsGeneratedThisMonth(0);
        dbUser.setLimitResetAt(java.time.LocalDateTime.now().plusMonths(1));
        userRepository.save(dbUser);

        String token = jwtUtil.generateToken(dbUser.getEmail(), dbUser.getRole(), dbUser.getId());
        
        Map<String, Object> response = new java.util.HashMap<>();
        response.put("message", "Subscribed to " + plan + " plan successfully!");
        response.put("token", token);
        response.put("role", dbUser.getRole());
        response.put("subscriptionPlan", dbUser.getSubscriptionPlan());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/profile")
    public ResponseEntity<?> getProfile() {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (principal instanceof User) {
            User principalUser = (User) principal;
            java.util.Optional<User> userOpt = userRepository.findById(principalUser.getId());
            if (userOpt.isPresent()) {
                User dbUser = userOpt.get();
                dbUser.checkSubscriptionStatus();
                dbUser.checkAndResetLimits();
                userRepository.save(dbUser);
                return ResponseEntity.ok(dbUser);
            }
        }
        return ResponseEntity.status(401).build();
    }

    @GetMapping("/dashboards/history")
    public ResponseEntity<List<DashboardHistory>> getHistory() {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (!(principal instanceof User)) {
            return ResponseEntity.status(401).build();
        }

        User user = (User) principal;
        List<DashboardHistory> history = dashboardHistoryRepository.findTop3ByUserOrderByCreatedAtDesc(user);
        return ResponseEntity.ok(history);
    }

    @PostMapping("/dashboards/history")
    public ResponseEntity<?> createHistory(@RequestBody Map<String, String> body) {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (!(principal instanceof User)) {
            return ResponseEntity.status(401).build();
        }
        User user = (User) principal;

        java.util.Optional<User> userOpt = userRepository.findById(user.getId());
        if (!userOpt.isPresent()) {
            return ResponseEntity.status(404).build();
        }
        User dbUser = userOpt.get();

        if (!dbUser.incrementGeneration()) {
            Map<String, Object> response = new java.util.HashMap<>();
            response.put("limit_reached", true);
            response.put("error", "You have reached your monthly dashboard generation limit. Please upgrade to a higher plan.");
            return ResponseEntity.status(403).body(response);
        }
        userRepository.save(dbUser);

        String rowCountStr = body.get("rowCount");
        Integer rowCount = rowCountStr != null ? Integer.parseInt(rowCountStr) : 0;

        DashboardHistory history = new DashboardHistory(
            dbUser,
            body.getOrDefault("datasetName", "Unknown"),
            rowCount,
            body.getOrDefault("cleaningSummary", ""),
            body.getOrDefault("kpiSummary", ""),
            body.getOrDefault("insights", "")
        );
        dashboardHistoryRepository.save(history);
        return ResponseEntity.ok(history);
    }


    private void seedSampleHistory(User user) {
        DashboardHistory h1 = new DashboardHistory(
            user,
            "sales_data_may_2026.csv",
            12450,
            "Removed 12 duplicates; handled null values in Product_Category.",
            "{\"total_revenue\": 145200.0, \"total_sales\": 3200, \"average_order\": 45.3}",
            "Top-performing product category is Electronics. West region shows a 14% growth in sales compared to last month."
        );

        DashboardHistory h2 = new DashboardHistory(
            user,
            "customer_churn_q1.csv",
            3200,
            "Cleaned column names; encoded churn labels (0/1).",
            "{\"churn_rate\": 0.18, \"active_customers\": 2624, \"lost_customers\": 576}",
            "High correlation detected between contract type (Monthly) and churn. Support ticket volume is a key leading indicator."
        );

        DashboardHistory h3 = new DashboardHistory(
            user,
            "product_inventory_v2.csv",
            8910,
            "Removed negative stock levels; filled missing restock times.",
            "{\"total_items\": 8910, \"out_of_stock\": 42, \"low_stock_warnings\": 120}",
            "Central warehouse is running at 94% capacity. Recommendations: trigger restocking for Category B items immediately."
        );

        dashboardHistoryRepository.save(h1);
        dashboardHistoryRepository.save(h2);
        dashboardHistoryRepository.save(h3);
    }
}
