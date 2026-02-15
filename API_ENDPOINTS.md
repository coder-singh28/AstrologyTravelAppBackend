# API Endpoints Documentation - Updated January 21, 2026

## Overview
RESTful API for Astrology Travel App - provides travel prediction based on Vedic astrology principles.

**Base URL:** http://127.0.0.1:8080

---

## Authentication Endpoints (/api/auth/*)

### 1. Google OAuth2 Login
**Endpoint:** GET /api/auth/google/login
**Description:** Initiate Google OAuth2 login flow. Redirects user to Google consent screen.

### 2. OAuth2 Callback Handler
**Endpoint:** GET /api/auth/callback
**Description:** Handle Google OAuth2 callback and create session.

### 3. Verify Google Token & Create Session
**Endpoint:** POST /api/auth/google/verify-token
**Description:** Verify Google ID token and authenticate user.

**Request Body:** { "token": "google_token_here" }

**Response:** User data with session_token, email, full_name, dob, tob, birth_place

---

## User Endpoints (/api/users/*)

### 4. Get User Details
**Endpoint:** POST /api/users/details
**Description:** Retrieve authenticated user details by session token.

**Request Body:** { "user_id": "123", "session_token": "token_here" }

---

## City Search Endpoints (/api/cities/*)

### 5. Search Cities (GET)
**Endpoint:** GET /api/cities/{prefix}
**Description:** Search for cities by name prefix (minimum 3 characters).

### 6. Search Cities (POST)
**Endpoint:** POST /api/cities/search
**Description:** Search for cities by name prefix using POST request.

---

## Astrology Endpoints (/api/astro/*)

### 7. Get Latitude & Longitude
**Endpoint:** POST /api/astro/get_lat_long
**Description:** Get latitude and longitude coordinates for a place.

### 8. Predict Travel Auspiciousness
**Endpoint:** POST /api/astro/predict_travel
**Description:** Predict auspiciousness of travel between two locations.

### 9. Analyse Journey
**Endpoint:** POST /api/astro/analyse_journey
**Description:** Analyze astrological aspects of a journey based on tithi and direction.

---

## File Changes (January 21, 2026)

### Renamed Files
- google_router.py  uth_router.py

### Updated Endpoints
- GET /loginWithGoogle  GET /api/auth/google/login
- POST /auth/verify  POST /api/auth/google/verify-token
- GET /home  GET /api/user/dashboard

---

**Last Updated:** January 21, 2026
**API Version:** 1.0.0
