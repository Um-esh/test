# BuddyShop - E-Commerce Platform

A fully-featured e-commerce platform similar to BuddyShop with Flask backend and responsive frontend.

## Features

✅ **Custom Authentication System**
- Email verification with 15-minute expiry
- Token-based authentication with user ID and login timestamp
- Forced logout via email confirmation
- Secure password hashing

✅ **E-Commerce Functionality**
- Product browsing with category filters and search
- Shopping cart management
- Order processing and tracking
- Seller dashboard for product management

✅ **Interactive Maps**
- OpenStreetMap integration with Leaflet.js
- Click to select delivery address
- Reverse geocoding for address lookup

✅ **Push Notifications**
- Firebase Cloud Messaging integration
- Real-time order updates

✅ **Responsive Design**
- Mobile-friendly interface
- Clean, modern UI inspired by BuddyShop
- Smooth animations and transitions

## Quick Start

1. **Configure Email (Optional)**
   - Set `MAIL_USERNAME` and `MAIL_PASSWORD` environment variables
   - Without email config, the app works but shows warnings

2. **Configure Firebase (Optional)**
   - Update Firebase config in `static/js/main.js`
   - Update service worker in `static/firebase-messaging-sw.js`

3. **Access the Application**
   - The app runs automatically on port 5000
   - Click the "Open Website" button or navigate to the Webview

## User Guide

### For Buyers
1. **Register**: Click "Register" and fill in your details
2. **Verify Email**: Check your email and click verification link (15 min window)
3. **Browse**: Explore products by category or search
4. **Add to Cart**: Select products and quantities
5. **Checkout**: Choose delivery address on interactive map
6. **Track Orders**: View order status in "My Orders"

### For Sellers
1. **Register as Seller**: Choose "Sell Products" during registration
2. **Access Dashboard**: After login, go to "Dashboard"
3. **Add Products**: Fill in product details and upload images
4. **Manage Inventory**: View and track your products

## Technical Details

### Authentication Flow
- Registration saves to temporary database
- Email verification moves user to main database (15-minute expiry)
- Login creates unique token: `hash(user_id + timestamp + random)`
- Token stored in httpOnly cookie
- Logout requires email confirmation

### Database Schema
- **users**: Main user table
- **temp_users**: Pending registrations (auto-cleanup every 5 minutes)
- **auth_tokens**: Active session tokens
- **products**: Product catalog
- **cart**: Shopping cart items
- **orders**: Order history with delivery info

### Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Email**: Flask-Mail with SMTP
- **Maps**: Leaflet.js + OpenStreetMap
- **Notifications**: Firebase Cloud Messaging
- **Styling**: Custom CSS (BuddyShop-inspired)

## Configuration

### Email Setup (Gmail)
1. Enable 2-factor authentication on your Gmail
2. Generate app-specific password
3. Set environment variables:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

### Firebase Setup (Optional - for Push Notifications)
1. Create Firebase project: https://console.firebase.google.com
2. Enable Cloud Messaging
3. Get config from Project Settings > General
4. Set the following environment variables:
   - `FIREBASE_API_KEY`: Your Firebase API key
   - `FIREBASE_AUTH_DOMAIN`: Your auth domain (project-id.firebaseapp.com)
   - `FIREBASE_PROJECT_ID`: Your project ID
   - `FIREBASE_STORAGE_BUCKET`: Your storage bucket
   - `FIREBASE_MESSAGING_SENDER_ID`: Your sender ID
   - `FIREBASE_APP_ID`: Your app ID
   - `FIREBASE_VAPID_KEY`: Get this from Project Settings > Cloud Messaging > Web Push certificates

The app will automatically detect if Firebase is configured and enable notifications accordingly.

## Screenshots Features

- 🏠 Modern homepage with category browsing
- 📦 Product detail pages with image galleries
- 🛒 Shopping cart with quantity management
- 🗺️ Interactive checkout with OpenStreetMap
- 👤 User authentication with email verification
- 🏪 Seller dashboard for product management
- 📱 Fully responsive mobile design

## Security

- Passwords hashed with Werkzeug
- HttpOnly cookies prevent XSS
- Email verification prevents spam
- File upload validation
- SQL injection protection via parameterized queries

## Support

For issues or questions, check the `replit.md` file for detailed documentation.

## License

This project is created for educational purposes.
