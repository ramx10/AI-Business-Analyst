package com.example.analytics.repository;

import com.example.analytics.model.DashboardHistory;
import com.example.analytics.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DashboardHistoryRepository extends JpaRepository<DashboardHistory, Long> {
    List<DashboardHistory> findTop3ByUserOrderByCreatedAtDesc(User user);
}
