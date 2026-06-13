package com.example.analytics.service;

import org.springframework.stereotype.Service;
import java.util.logging.Logger;

@Service
public class PaymentGatewayService {

    private static final Logger logger = Logger.getLogger(PaymentGatewayService.class.getName());

    public static class PaymentResult {
        private final boolean success;
        private final String transactionId;
        private final String errorMessage;

        public PaymentResult(boolean success, String transactionId, String errorMessage) {
            this.success = success;
            this.transactionId = transactionId;
            this.errorMessage = errorMessage;
        }

        public boolean isSuccess() { return success; }
        public String getTransactionId() { return transactionId; }
        public String getErrorMessage() { return errorMessage; }
    }

    /**
     * Process a simulated subscription payment.
     */
    public PaymentResult processPayment(String plan, double amount, String method, String token) {
        logger.info(String.format("Processing payment of $%f for plan %s via %s (token: %s)", amount, plan, method, token));

        // Simulated validation logic
        if (token == null || token.trim().isEmpty()) {
            return new PaymentResult(false, null, "Payment token is missing.");
        }

        if (token.contains("decline") || token.contains("fail")) {
            return new PaymentResult(false, null, "Card was declined. Please try another card.");
        }

        String transactionId = method.toUpperCase() + "_" + java.util.UUID.randomUUID().toString().substring(0, 18);
        logger.info("Payment successful. Transaction ID: " + transactionId);
        return new PaymentResult(true, transactionId, null);
    }
}
