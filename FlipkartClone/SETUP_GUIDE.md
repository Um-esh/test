# BuddyShop Setup Guide

This guide will walk you through setting up all the features of your e-commerce platform.

## Basic Setup (Already Done!)

The application is ready to use immediately! The basic features work out of the box:
- ✅ User registration and login
- ✅ Product browsing and search
- ✅ Shopping cart
- ✅ Order placement
- ✅ Seller dashboard
- ✅ Map-based address selection

## Optional: Email Configuration

Enable email verification and logout confirmation by setting up SMTP.

### Using Gmail

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Set Environment Variables** in Replit:
   - Go to Secrets (lock icon in left sidebar)
   - Add `MAIL_USERNAME`: your-email@gmail.com
   - Add `MAIL_PASSWORD`: your-16-character-app-password

### Using Other SMTP Servers

Update `app.py` with your SMTP settings:
```python
app.config['MAIL_SERVER'] = 'smtp.yourserver.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
```

Then set the environment variables:
- `MAIL_USERNAME`: your email
- `MAIL_PASSWORD`: your password

## Optional: Firebase Push Notifications

Enable real-time notifications for orders and updates.

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project"
3. Name it (e.g., "buddyshop-notifications")
4. Disable Google Analytics (not needed)
5. Create project

### Step 2: Enable Cloud Messaging

1. In your Firebase project, click the gear icon → Project settings
2. Go to "Cloud Messaging" tab
3. Under "Web Push certificates", click "Generate key pair"
4. Save the VAPID key that appears

### Step 3: Get Firebase Configuration

1. In Project settings → General tab
2. Scroll to "Your apps" section
3. Click the web icon (`</>`) to add a web app
4. Register app with a nickname (e.g., "buddyshop-web")
5. Copy the configuration values shown

### Step 4: Set Environment Variables

Add these to your Replit Secrets:

```
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123
FIREBASE_VAPID_KEY=BNx... (from Step 2)
```

### Step 5: Test Notifications

1. Register and login to your app
2. Open browser console (F12)
3. You should see "FCM Token obtained" message
4. Notifications are now enabled!

### Sending Test Notifications

Use Firebase Console:
1. Go to Cloud Messaging → Send your first message
2. Enter notification text
3. Click "Send test message"
4. Paste your FCM token from browser console
5. Click "Test"

## Security Features Explained

### 1. Email Verification (15-minute window)
- User registers → data saved to temporary database
- Verification email sent with unique link
- User clicks link within 15 minutes → moved to main database
- After 15 minutes, registration expires (auto-cleanup runs every 5 minutes)

### 2. Secure Login Tokens
- Token = `SHA256(user_id + login_timestamp + random_32_bytes)`
- Stored in httpOnly cookies (JavaScript can't access)
- Each login creates a new unique token
- Old tokens invalidated on logout

### 3. Forced Logout Protection
- Logout request generates secure random token
- Token stored in database with 15-minute expiry
- Email sent with token link
- Token is single-use and validated before logout
- Prevents unauthorized forced logouts

### 4. Password Security
- Passwords hashed with Werkzeug's PBKDF2
- Salted and iterated for strong protection
- Never stored or logged in plain text

## Testing the Application

### Test User Registration

1. Go to Register page
2. Fill in details
3. Choose "Buy Products" or "Sell Products"
4. Submit form
5. Check email for verification link (if configured)
6. Or use the user_id from console to manually verify

### Test Seller Features

1. Register as seller
2. Login
3. Click "Dashboard" in navigation
4. Click "Add New Product"
5. Fill in product details and upload images
6. Submit
7. Product appears on homepage

### Test Shopping Flow

1. Browse products on homepage
2. Click product to view details
3. Click "Add to Cart"
4. Go to Cart
5. Click "Proceed to Checkout"
6. Click on map to select delivery address
7. Fill in address details
8. Place order
9. View in "My Orders"

## Troubleshooting

### Email Not Sending
- Check MAIL_USERNAME and MAIL_PASSWORD are set correctly
- For Gmail, ensure app password (not regular password)
- Check spam folder
- App works without email, shows console warnings

### Firebase Not Working
- Verify all 7 environment variables are set
- Check browser console for errors
- Ensure VAPID key is from "Web Push certificates"
- Service worker must be on HTTPS (Replit provides this)

### Database Issues
- Database auto-creates on first run
- If corrupt, delete `ecommerce.db` and restart
- Temporary data cleaned up every 5 minutes

### Images Not Uploading
- Check file size (max 16MB)
- Supported formats: PNG, JPG, JPEG, GIF, WEBP
- `static/uploads/` folder created automatically

## Production Deployment

When publishing your app:

1. **Use Production WSGI Server**:
   - Currently using Flask dev server
   - For production, use gunicorn or waitress
   - Update workflow command: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

2. **Disable Debug Mode**:
   - Set `debug=False` in `app.py`
   - Or set environment variable `FLASK_ENV=production`

3. **Secure Session Secret**:
   - Set `SESSION_SECRET` environment variable
   - Use strong random value: `python -c "import secrets; print(secrets.token_hex(32))"`

4. **Database Backups**:
   - SQLite database is in `ecommerce.db`
   - Download regularly for backups
   - Consider PostgreSQL for production scaling

## Next Steps

Want to enhance your platform? Consider:

- **Payment Integration**: Add Stripe or PayPal
- **Reviews & Ratings**: Let buyers review products
- **Advanced Search**: Full-text search with filters
- **Seller Analytics**: Sales graphs and insights
- **Inventory Alerts**: Notify when stock is low
- **Wishlist**: Save products for later
- **Order Tracking**: Real-time delivery status
- **Multiple Images**: Gallery view for products
- **Product Variants**: Sizes, colors, etc.

## Support

Check `replit.md` for technical documentation and architecture details.
