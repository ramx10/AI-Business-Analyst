package com.example.analytics.config;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Date;

@Component
public class JwtUtil {

    private static final String SECRET = "my-super-secret-jwt-key-256-bit-minimum-requirement-for-hmac";
    private static final long EXPIRATION_TIME = 86400000; // 24 hours in milliseconds

    private final Algorithm algorithm = Algorithm.HMAC256(SECRET);

    public String generateToken(String email, String role, Long id) {
        return JWT.create()
                .withSubject(email)
                .withClaim("role", role)
                .withClaim("id", id)
                .withIssuedAt(new Date())
                .withExpiresAt(new Date(System.currentTimeMillis() + EXPIRATION_TIME))
                .sign(algorithm);
    }

    public DecodedJWT validateToken(String token) {
        JWTVerifier verifier = JWT.require(algorithm).build();
        return verifier.verify(token);
    }

    public String getEmailFromToken(String token) {
        return validateToken(token).getSubject();
    }

    public String getRoleFromToken(String token) {
        return validateToken(token).getClaim("role").asString();
    }

    public Long getIdFromToken(String token) {
        return validateToken(token).getClaim("id").asLong();
    }
}
