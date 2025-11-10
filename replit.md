# Buddy-Shop E-Commerce Platform

## Overview

Buddy-Shop is a comprehensive e-commerce platform with a professional cold-war inspired 3D design aesthetic, built with Flask backend and vanilla JavaScript frontend. The platform supports both global e-commerce and local marketplace modes, allowing users to shop from anywhere or discover nearby sellers within a 30km radius. It features a custom token-based authentication system, seller product management, shopping cart functionality, order processing, and integrated map-based address selection.

## Recent Updates (November 2025)

**Complete Design Overhaul - Cold War Professional Theme**
- Implemented military-inspired color palette: olive greens (#556B2F), burgundy (#6B2C2C), tan/beige (#D4C5B0), and metallic grays
- Added comprehensive 3D depth effects throughout the UI using multi-layer box shadows and gradients
- Created stunning onboarding screen with animated logo, military badges, and fade-out transition
- Rebranded entire application from "FlipShop" to "Buddy-Shop" with new logo integration
- Updated all UI components (navbar, buttons, cards, forms) with raised/embossed 3D styling
- Implemented 3D utility classes: .elevated, .inset, .glossy, .metallic for consistent depth application
- All gradients and shadows follow the cold-war professional aesthetic with proper depth perception

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework & Core Technologies**
- **Flask**: Python web framework serving as the application backbone
- **SQLAlchemy ORM**: Database abstraction layer for data management
- **SQLite**: Lightweight embedded database for data persistence
- **Werkzeug**: Security utilities for password hashing and file uploads

**Custom Authentication System**
The application implements a multi-stage authentication flow:
1. **Registration Flow**: User data is temporarily stored in a `temp_users` table with 15-minute expiry
2. **Email Verification**: Users receive verification emails and must confirm within the time window
3. **User Migration**: Upon verification, data moves from temporary to permanent `users` table
4. **Token Generation**: Login creates unique tokens combining user ID, timestamp, and random data hashed with SHA-256
5. **Session Management**: Tokens stored in HTTP-only cookies for security
6. **Forced Logout**: Email confirmation required for logout, setting `login_status` flag to false

**Rationale**: This custom system provides granular control over user lifecycle, prevents spam registrations through email verification, and adds extra security through email-confirmed logout. Alternative considered was using Flask-Login, but custom solution offers more flexibility for multi-device session management.

**Background Task Scheduler**
- **APScheduler**: Runs cleanup jobs every 5 minutes to remove expired temporary users and logout tokens
- Prevents database bloat from abandoned registrations

### Frontend Architecture

**Technology Stack**
- Pure HTML5/CSS3/JavaScript (no frontend framework)
- Leaflet.js for interactive maps with OpenStreetMap integration
- Firebase SDK for push notifications
- Font Awesome for iconography

**Rationale**: Vanilla JavaScript chosen for simplicity and performance. No build step required, faster initial load times, and easier deployment. Considered React/Vue but deemed unnecessary for the scope.

**Key Frontend Features**
1. **Dual Mode System**: Toggle between global e-commerce and local marketplace (30km radius)
2. **Interactive Address Selection**: Click-to-select on map with reverse geocoding
3. **Real-time Cart Management**: Asynchronous cart updates without page reload
4. **Responsive Design**: Mobile-first approach with flexible grid layouts

### Database Schema Design

**Core Tables**
- `temp_users`: Temporary storage for unverified registrations (15-min TTL)
- `users`: Permanent user accounts with seller shop location data
- `auth_tokens`: Session tokens linked to users with login timestamps
- `logout_tokens`: Email-confirmed logout tokens with expiry
- `products`: Product catalog with seller references, images stored as JSON array
- `cart`: Shopping cart items linked to users and products
- `orders`: Order records with JSON-serialized product lists
- `addresses`: Saved delivery addresses with geocoordinates

**Design Decisions**
- Separate temporary and permanent user tables prevent polluting main user base
- Shop location fields (latitude, longitude, city, pincode) enable radius-based local search
- JSON fields for product images and order items provide flexibility without additional tables
- FCM token field in users table supports push notifications

**Alternative Considered**: PostgreSQL with proper relational design for order items. Chose SQLite with JSON for simplicity and portability in development. Migration path exists for production scaling.

### File Upload System

**Configuration**
- Upload folder: `static/uploads`
- Allowed formats: PNG, JPG, JPEG, GIF, WEBP
- Maximum file size: 16MB
- Multiple image upload support per product

**Processing**: Werkzeug's `secure_filename` sanitizes uploads, files stored with original names in upload directory, paths stored as JSON array in database.

### Email System

**Flask-Mail Integration**
- SMTP server: Gmail (configurable)
- TLS encryption enabled
- Use cases: Email verification, logout confirmation, password reset

**Configuration**: Supports environment variables for credentials (`MAIL_USERNAME`, `MAIL_PASSWORD`). Falls back gracefully if not configured, showing warnings but allowing app to function.

## External Dependencies

### Third-Party APIs & Services

**OpenStreetMap & Leaflet.js**
- **Purpose**: Interactive map display and address selection
- **Integration**: Client-side JavaScript library rendering OSM tiles
- **Features**: Click-to-select location, reverse geocoding via Nominatim API
- **Rationale**: Free, open-source alternative to Google Maps. No API keys required. Lightweight integration.

**Firebase Cloud Messaging (FCM)**
- **Purpose**: Push notifications for order updates and real-time alerts
- **Configuration**: Requires Firebase project setup with API keys
- **Implementation**: Service worker for background message handling
- **Status**: Optional - app functions without Firebase configuration

**Nominatim Reverse Geocoding API**
- **Purpose**: Convert latitude/longitude to human-readable addresses
- **Provider**: OpenStreetMap's geocoding service
- **Usage**: Address lookup during map-based selection
- **Rate Limits**: Subject to Nominatim usage policy

### Python Package Dependencies

**Core Dependencies**
- `flask`: Web framework
- `flask-sqlalchemy`: ORM integration
- `flask-mail`: Email functionality
- `werkzeug`: Security and utilities
- `apscheduler`: Background job scheduling
- `pillow`: Image processing (for future enhancements)

**Database**: SQLite (no external database server required)

### Frontend Libraries (CDN-loaded)

- **Leaflet.js** (v1.9.4): Map rendering
- **Font Awesome** (v6.4.0): Icon library
- **Firebase SDK** (v10.7.1): Push notifications

**Rationale for CDN**: Reduces deployment complexity, leverages browser caching, faster updates. Alternative was npm/bundler approach but adds build complexity.

### Environment Variables

**Required for Full Functionality**
- `MAIL_USERNAME`: SMTP email address
- `MAIL_PASSWORD`: SMTP password or app-specific token
- `SESSION_SECRET`: Flask session encryption key (auto-generated if missing)

**Optional**
- Firebase configuration keys (for push notifications)
- Custom SMTP server settings

### SMTP Provider Options

**Current Default**: Gmail with app passwords
**Alternatives Supported**: Any SMTP server (SendGrid, Mailgun, custom)
**Fallback Behavior**: App warns about missing email config but remains functional for core shopping features