package com.example.analytics.controller;

import com.example.analytics.model.User;
import com.example.analytics.model.DashboardHistory;
import com.example.analytics.repository.UserRepository;
import com.example.analytics.repository.DashboardHistoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DashboardHistoryRepository dashboardHistoryRepository;

    @GetMapping("/profile")
    public ResponseEntity<User> getProfile() {
        // Retrieve the authenticated user from the Security Context
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (principal instanceof User) {
            return ResponseEntity.ok((User) principal);
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

        // Return empty list if no history exists
        // (We no longer seed mock data to avoid confusing users)

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
