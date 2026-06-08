package com.example.analytics.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "dashboard_history")
public class DashboardHistory {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "dataset_name", nullable = false)
    private String datasetName;
    
    @Column(name = "row_count")
    private Integer rowCount;
    
    @Column(name = "cleaning_summary", columnDefinition = "TEXT")
    private String cleaningSummary;
    
    @Column(name = "kpi_summary", columnDefinition = "TEXT") // Store JSON as String/TEXT
    private String kpiSummary;
    
    @Column(columnDefinition = "TEXT")
    private String insights;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    // Constructors
    public DashboardHistory() {}

    public DashboardHistory(User user, String datasetName, Integer rowCount, String cleaningSummary, String kpiSummary, String insights) {
        this.user = user;
        this.datasetName = datasetName;
        this.rowCount = rowCount;
        this.cleaningSummary = cleaningSummary;
        this.kpiSummary = kpiSummary;
        this.insights = insights;
        this.createdAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public String getDatasetName() { return datasetName; }
    public void setDatasetName(String datasetName) { this.datasetName = datasetName; }

    public Integer getRowCount() { return rowCount; }
    public void setRowCount(Integer rowCount) { this.rowCount = rowCount; }

    public String getCleaningSummary() { return cleaningSummary; }
    public void setCleaningSummary(String cleaningSummary) { this.cleaningSummary = cleaningSummary; }

    public String getKpiSummary() { return kpiSummary; }
    public void setKpiSummary(String kpiSummary) { this.kpiSummary = kpiSummary; }

    public String getInsights() { return insights; }
    public void setInsights(String insights) { this.insights = insights; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
