# BuddyShop E-Commerce Platform

## Project Overview
A comprehensive e-commerce platform similar to BuddyShop, built with Flask backend and modern HTML/CSS/JavaScript frontend. Features include custom token-based authentication, seller product management, shopping cart, order processing, and integrated mapping for delivery addresses.

## Recent Changes
- **Date: November 9, 2024**
  - Initial project setup with complete e-commerce functionality
  - Implemented custom authentication system with email verification
  - Created responsive UI inspired by BuddyShop
  - Integrated OpenStreetMap with Leaflet.js for address selection
  - Set up Firebase Cloud Messaging for push notifications

## Technology Stack

### Backend
- **Flask**: Web framework for Python
- **SQLite**: Database for users, products, orders, and cart
- **Flask-Mail**: Email verification and logout confirmation
- **APScheduler**: Background task scheduling for temp user cleanup
- **Werkzeug**: Password hashing and security
- **Pillow**: Image processing for product uploads

### Frontend
- **HTML5/CSS3**: Structure and styling
- **JavaScript (Vanilla)**: Interactive functionality
- **Leaflet.js**: OpenStreetMap integration for delivery addresses
- **Firebase SDK**: Push notifications
- **Font Awesome**: Icons

## Project Architecture

### Database Structure
- **temp_users**: Temporary user storage with 15-minute expiry for email verification
- **users**: Main user table with login status tracking
- **auth_tokens**: Authentication tokens with user ID and login timestamp
- **products**: Product catalog with seller information
- **cart**: Shopping cart items
- **orders**: Order history with delivery information
- **addresses**: Saved delivery addresses with coordinates

### Authentication System
1. **Registration**: User data saved to temp database, verification email sent
2. **Email Verification**: 15-minute window to click link and move to main database
3. **Login**: Generates unique token based on user ID + login timestamp
4. **Session**: Token stored in httpOnly cookie for security
5. **Logout**: Email confirmation required, sets login_status to false

### Key Features
1. **User Management**: Registration with email verification, token-based auth
2. **Seller Dashboard**: Add/manage products with image uploads
3. **Product Catalog**: Browse, search, filter by category
4. **Shopping Cart**: Add/remove items, quantity management
5. **Checkout**: Interactive map for address selection using OSM/Leaflet
6. **Order Tracking**: View order history with delivery status
7. **Notifications**: Firebase Cloud Messaging for real-time updates

## File Structure
```
.
├── app.py                  # Main Flask application
├── database.py            # Database models and initialization
├── auth.py                # Authentication utilities
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── verified.html     # Email verification result
│   ├── products.html     # Product listing
│   ├── product_detail.html
│   ├── seller_dashboard.html
│   ├── add_product.html
│   ├── cart.html
│   ├── checkout.html
│   └── orders.html
├── static/
│   ├── css/style.css     # Main stylesheet
│   ├── js/main.js        # JavaScript functionality
│   ├── firebase-messaging-sw.js
│   └── uploads/          # Product images
└── ecommerce.db          # SQLite database
```

## Environment Variables

### Required for Email Functionality
- `SESSION_SECRET`: Flask session secret (auto-generated if not set)
- `MAIL_USERNAME`: SMTP email username
- `MAIL_PASSWORD`: SMTP email password

### Optional for Firebase Push Notifications
- `FIREBASE_API_KEY`: Firebase API key
- `FIREBASE_AUTH_DOMAIN`: Firebase auth domain
- `FIREBASE_PROJECT_ID`: Firebase project ID
- `FIREBASE_STORAGE_BUCKET`: Firebase storage bucket
- `FIREBASE_MESSAGING_SENDER_ID`: Firebase messaging sender ID
- `FIREBASE_APP_ID`: Firebase app ID
- `FIREBASE_VAPID_KEY`: Firebase VAPID key for web push

If not configured, the app gracefully handles missing Firebase config.

## Setup Instructions

### 1. Email Configuration
To enable email verification and logout confirmation:
1. Set up a Gmail account or SMTP server
2. Add environment variables:
   - `MAIL_USERNAME`: Your email address
   - `MAIL_PASSWORD`: App password (for Gmail, create app-specific password)

### 2. Firebase Setup (Optional)
For push notifications:
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Cloud Messaging
3. Get your config from Project Settings
4. Update Firebase config in:
   - `static/js/main.js`
   - `static/firebase-messaging-sw.js`
5. Generate VAPID key from Cloud Messaging settings

### 3. Running the Application
The application runs automatically via the configured workflow on port 5000.

## User Workflows

### Buyer Journey
1. Register → Verify email (15 min window)
2. Login → Browse products
3. Add to cart → Checkout with map selection
4. Place order → Track in Orders page

### Seller Journey
1. Register as seller → Verify email
2. Login → Access seller dashboard
3. Add products with images
4. Manage inventory

## Security Features
- Password hashing with Werkzeug
- HttpOnly cookies for auth tokens
- CSRF protection via Flask
- Email verification required
- Forced logout with email confirmation
- Secure file upload validation

## API Endpoints

### Authentication
- `POST /register`: Create temp user, send verification email
- `GET /verify/<user_id>`: Verify email and move to main DB
- `POST /login`: Generate auth token, set cookies
- `POST /logout-request`: Send logout confirmation email
- `GET /logout-confirm/<user_id>`: Confirm logout

### Products
- `GET /`: Homepage with featured products
- `GET /products`: Product listing with filters
- `GET /product/<product_id>`: Product details
- `POST /seller/add-product`: Add new product (sellers only)
- `GET /api/categories`: Get all categories

### Cart & Orders
- `POST /cart/add`: Add item to cart
- `GET /cart`: View cart
- `POST /cart/remove/<cart_id>`: Remove from cart
- `POST /checkout`: Place order with delivery address
- `GET /orders`: View order history

## Future Enhancements
- Payment gateway integration (Stripe/PayPal)
- Product reviews and ratings
- Real-time inventory management
- Admin panel for platform management
- Advanced product recommendation engine
- Multi-vendor rating system
