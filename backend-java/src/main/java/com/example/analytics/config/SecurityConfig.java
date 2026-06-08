package com.example.analytics.config;

import com.example.analytics.model.User;
import com.example.analytics.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.client.oidc.userinfo.OidcUserService;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.Optional;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private UserRepository userRepository;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/user/**").authenticated()
                .anyRequest().permitAll()
            )
            .oauth2Login(oauth2 -> oauth2
                .successHandler(new OAuth2SuccessHandler())
                .userInfoEndpoint(userInfo -> userInfo
                    .oidcUserService(oidcUserService())
                    .userService(oauth2UserService())
                )
            )
            .addFilterBefore(tokenAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("http://localhost:8000", "http://127.0.0.1:8000"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Cache-Control", "Content-Type"));
        configuration.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public OidcUserService oidcUserService() {
        OidcUserService delegate = new OidcUserService();
        return new OidcUserService() {
            @Override
            public OidcUser loadUser(org.springframework.security.oauth2.client.oidc.userinfo.OidcUserRequest userRequest) 
                    throws OAuth2AuthenticationException {
                OidcUser oidcUser = delegate.loadUser(userRequest);
                
                String googleId = oidcUser.getSubject();
                String email = oidcUser.getEmail();
                String name = oidcUser.getFullName();
                String pictureUrl = oidcUser.getPicture();
                
                // Save or update user profile details in database
                saveOrUpdateUser(googleId, email, name, pictureUrl);
                
                return oidcUser;
            }
        };
    }

    @Bean
    public OAuth2UserService<OAuth2UserRequest, OAuth2User> oauth2UserService() {
        DefaultOAuth2UserService delegate = new DefaultOAuth2UserService();
        return userRequest -> {
            OAuth2User oauth2User = delegate.loadUser(userRequest);
            
            String googleId = oauth2User.getName();
            String email = oauth2User.getAttribute("email");
            String name = oauth2User.getAttribute("name");
            String pictureUrl = oauth2User.getAttribute("picture");
            
            saveOrUpdateUser(googleId, email, name, pictureUrl);
            
            return oauth2User;
        };
    }

    private void saveOrUpdateUser(String googleId, String email, String name, String pictureUrl) {
        Optional<User> existingUser = userRepository.findByEmail(email);
        if (existingUser.isPresent()) {
            User user = existingUser.get();
            user.setName(name);
            user.setPictureUrl(pictureUrl);
            user.setUpdatedAt(LocalDateTime.now());
            userRepository.save(user);
        } else {
            User newUser = new User(googleId, email, name, pictureUrl);
            userRepository.save(newUser);
        }
    }

    @Bean
    public OncePerRequestFilter tokenAuthenticationFilter() {
        return new OncePerRequestFilter() {
            @Override
            protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
                    throws ServletException, IOException {
                String header = request.getHeader("Authorization");
                if (header != null && header.startsWith("Bearer ")) {
                    String token = header.substring(7);
                    
                    // Simple Token validation: looks up database by email token
                    Optional<User> userOpt = userRepository.findByEmail(token);
                    if (userOpt.isPresent()) {
                        User user = userOpt.get();
                        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                                user, null, Collections.emptyList());
                        SecurityContextHolder.getContext().setAuthentication(auth);
                    }
                }
                filterChain.doFilter(request, response);
            }
        };
    }

    // Redirects to frontend with ?token=email on successful login
    public static class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {
        @Override
        public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                Authentication authentication) throws IOException, ServletException {
            OAuth2User oauth2User = (OAuth2User) authentication.getPrincipal();
            String email = oauth2User.getAttribute("email");
            
            String targetUrl = UriComponentsBuilder.fromUriString("http://localhost:8000/index.html")
                    .queryParam("token", email)
                    .build().toUriString();
            getRedirectStrategy().sendRedirect(request, response, targetUrl);
        }
    }
}
