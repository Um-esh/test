from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, send_from_directory
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import secrets
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db, get_db_connection, cleanup_expired_temp_users
from auth import create_temp_user, verify_and_move_user, create_auth_token, verify_token, logout_user, generate_user_id, create_logout_token, verify_logout_token

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET',
                                          secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'srms.inventory@gmail.com'
app.config['MAIL_PASSWORD'] = 'ilslkasxuyqcqnke'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME',
                                                   'noreply@ecommerce.com')

mail = Mail(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_expired_temp_users,
                  trigger="interval",
                  minutes=5)
scheduler.start()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_user():
    token = request.cookies.get('auth_token')
    user_id = request.cookies.get('user_id')

    if token and user_id:
        verified_user_id = verify_token(token)
        if verified_user_id == user_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?',
                           (user_id, ))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
    return None


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT 20')
    products = [dict(row) for row in cursor.fetchall()]

    for product in products:
        if product['images']:
            product['images'] = json.loads(product['images'])

    conn.close()

    user = get_current_user()
    return render_template('index.html', products=products, user=user)


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one capital letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Valid"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        phone = data.get('phone')
        user_type = data.get('user_type', 'buyer')

        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': message})

        password_hash = generate_password_hash(password)
        user_id = create_temp_user(email, password_hash, full_name, phone,
                                   user_type)

        if user_id:
            verification_link = f"{request.host_url}verify/{user_id}"

            try:
                msg = Message('Verify Your Email - E-Commerce',
                              recipients=[email])
                msg.html = f'''
                <h2>Welcome to Our E-Commerce Platform!</h2>
                <p>Hi {full_name},</p>
                <p>Thank you for registering. Please verify your email within 15 minutes by clicking the link below:</p>
                <p><a href="{verification_link}" style="background-color: #2874f0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
                <p>If the button doesn't work, copy and paste this link: {verification_link}</p>
                <p>This link will expire in 15 minutes.</p>
                '''
                mail.send(msg)
                return jsonify({
                    'success':
                    True,
                    'message':
                    'Registration successful! Check your email to verify.'
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'message':
                    'Registration successful! (Email service not configured)',
                    'user_id': user_id
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            })

    return render_template('register.html')


@app.route('/verify/<user_id>')
def verify_email(user_id):
    if verify_and_move_user(user_id):
        return render_template('verified.html', success=True)
    else:
        return render_template('verified.html', success=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        force_login = data.get('force_login', False)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email, ))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            if user['login_status'] == 1 and not force_login:
                try:
                    msg = Message('New Login Attempt', recipients=[user['email']])
                    msg.html = f'''
                    <h2>New Login Attempt Detected</h2>
                    <p>Hi {user['full_name']},</p>
                    <p>Someone is trying to log into your account from a new device/browser.</p>
                    <p>If this was you, please confirm the login in your browser.</p>
                    <p>If this wasn't you, your account may be at risk. Please change your password immediately.</p>
                    '''
                    mail.send(msg)
                except:
                    pass
                
                return jsonify({
                    'success': False,
                    'message': 'Account already logged in elsewhere',
                    'already_logged_in': True
                })
            
            token = create_auth_token(user['user_id'])

            response = make_response(
                jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'user': {
                        'user_id': user['user_id'],
                        'email': user['email'],
                        'full_name': user['full_name'],
                        'user_type': user['user_type']
                    }
                }))

            response.set_cookie('user_id',
                                user['user_id'],
                                max_age=30 * 24 * 60 * 60,
                                httponly=True)
            response.set_cookie('auth_token',
                                token,
                                max_age=30 * 24 * 60 * 60,
                                httponly=True)

            return response
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            })

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    user = get_current_user()

    if user:
        logout_user(user['user_id'])
        response = make_response(jsonify({'success': True, 'message': 'Logged out successfully'}))
        response.delete_cookie('user_id')
        response.delete_cookie('auth_token')
        return response

    return jsonify({'success': False, 'message': 'Not logged in'})

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            reset_token = create_logout_token(user['user_id'])
            reset_link = f"{request.host_url}reset-password/{reset_token}"
            
            try:
                msg = Message('Password Reset Request', recipients=[email])
                msg.html = f'''
                <h2>Password Reset Request</h2>
                <p>Hi {user['full_name']},</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}" style="background-color: #2874f0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                <p>This link will expire in 15 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                '''
                mail.send(msg)
                return jsonify({'success': True, 'message': 'Password reset link sent to your email'})
            except:
                return jsonify({'success': False, 'message': 'Email service not configured'})
        else:
            return jsonify({'success': True, 'message': 'If email exists, reset link has been sent'})
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        data = request.json
        new_password = data.get('password')
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        user_id = verify_logout_token(token)
        
        if user_id:
            password_hash = generate_password_hash(new_password)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE user_id = ?', (password_hash, user_id))
            cursor.execute('UPDATE auth_tokens SET is_active = 0 WHERE user_id = ?', (user_id,))
            cursor.execute('UPDATE users SET login_status = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Password reset successful! Please login.'})
        else:
            return jsonify({'success': False, 'message': 'Invalid or expired reset link'})
    
    user_id = verify_logout_token(token)
    if user_id:
        return render_template('reset_password.html', token=token)
    else:
        return render_template('verified.html', success=False)


@app.route('/products')
def products():
    category = request.args.get('category')
    search = request.args.get('search')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM products WHERE is_visible = 1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    if search:
        search_terms = search.split()
        conditions = []
        for term in search_terms:
            conditions.append(f'(name LIKE ? OR description LIKE ? OR category LIKE ?)')
            params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
        if conditions:
            query += ' AND (' + ' OR '.join(conditions) + ')'

    query += ' ORDER BY created_at DESC'

    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]

    for product in products:
        if product['images']:
            product['images'] = json.loads(product['images'])

    conn.close()

    user = get_current_user()
    return render_template('products.html', products=products, user=user)


@app.route('/product/<product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE product_id = ?',
                   (product_id, ))
    product = cursor.fetchone()
    conn.close()

    if product:
        product = dict(product)
        if product['images']:
            product['images'] = json.loads(product['images'])

        user = get_current_user()
        return render_template('product_detail.html',
                               product=product,
                               user=user)
    else:
        return "Product not found", 404


@app.route('/seller/dashboard')
def seller_dashboard():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE seller_id = ?',
                   (user['user_id'], ))
    products = [dict(row) for row in cursor.fetchall()]

    for product in products:
        if product['images']:
            product['images'] = json.loads(product['images'])

    conn.close()

    return render_template('seller_dashboard.html',
                           products=products,
                           user=user)


@app.route('/seller/add-product', methods=['GET', 'POST'])
def add_product():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        expiry_date = request.form.get('expiry_date', '')
        is_visible = request.form.get('is_visible', '1')

        product_id = f"PROD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        image_paths = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(
                        f"{product_id}_{secrets.token_hex(4)}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'],
                                            filename)
                    file.save(filepath)
                    image_paths.append(f"/static/uploads/{filename}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO products (product_id, seller_id, name, description, category, price, stock, images, is_visible, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, user['user_id'], name, description, category, price,
              stock, json.dumps(image_paths), int(is_visible), expiry_date))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Product added successfully!',
            'product_id': product_id
        })

    return render_template('add_product.html', user=user)

@app.route('/seller/update-product/<product_id>', methods=['POST'])
def update_product(product_id):
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    price = data.get('price')
    stock = data.get('stock')
    is_visible = data.get('is_visible')
    expiry_date = data.get('expiry_date')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT seller_id FROM products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product or product['seller_id'] != user['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    updates = []
    params = []
    
    if price is not None:
        updates.append('price = ?')
        params.append(float(price))
    if stock is not None:
        updates.append('stock = ?')
        params.append(int(stock))
    if is_visible is not None:
        updates.append('is_visible = ?')
        params.append(int(is_visible))
    if expiry_date is not None:
        updates.append('expiry_date = ?')
        params.append(expiry_date)
    
    if updates:
        query = f"UPDATE products SET {', '.join(updates)} WHERE product_id = ?"
        params.append(product_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

    return jsonify({'success': True, 'message': 'Product updated successfully'})

@app.route('/seller/orders')
def seller_orders():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT o.* FROM orders o
        WHERE EXISTS (
            SELECT 1 FROM products p
            WHERE p.seller_id = ? AND o.products LIKE '%' || p.product_id || '%'
        )
        ORDER BY o.created_at DESC
    ''', (user['user_id'],))
    
    orders = [dict(row) for row in cursor.fetchall()]
    
    for order in orders:
        order['products'] = json.loads(order['products'])
    
    conn.close()

    return render_template('seller_orders.html', orders=orders, user=user)


@app.route('/cart')
def cart():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT c.*, p.name, p.price, p.images
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    ''', (user['user_id'], ))

    cart_items = [dict(row) for row in cursor.fetchall()]

    for item in cart_items:
        if item['images']:
            item['images'] = json.loads(item['images'])

    conn.close()

    return render_template('cart.html', cart_items=cart_items, user=user)


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    user = get_current_user()

    if not user:
        return jsonify({
            'success': False,
            'message': 'Please login first'
        }), 401

    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
                   (user['user_id'], product_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            'UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
            (quantity, user['user_id'], product_id))
        message = 'Quantity updated in cart!'
    else:
        cursor.execute(
            'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
            (user['user_id'], product_id, quantity))
        message = 'Added to cart!'

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': message})

@app.route('/cart/check/<product_id>')
def check_cart(product_id):
    user = get_current_user()

    if not user:
        return jsonify({'in_cart': False})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', (user['user_id'], product_id))
    item = cursor.fetchone()
    conn.close()

    if item:
        return jsonify({'in_cart': True, 'quantity': item['quantity']})
    else:
        return jsonify({'in_cart': False})


@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    user = get_current_user()

    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE id = ? AND user_id = ?',
                   (cart_id, user['user_id']))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Removed from cart'})


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.json
        delivery_address = data.get('address')
        delivery_lat = data.get('latitude')
        delivery_lng = data.get('longitude')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT c.*, p.name, p.price
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
        ''', (user['user_id'], ))

        cart_items = [dict(row) for row in cursor.fetchall()]

        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})

        total_amount = sum(item['price'] * item['quantity']
                           for item in cart_items)
        order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        products_json = json.dumps([{
            'product_id': item['product_id'],
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price']
        } for item in cart_items])

        cursor.execute(
            '''
            INSERT INTO orders (order_id, user_id, products, total_amount, delivery_address, delivery_lat, delivery_lng)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, user['user_id'], products_json, total_amount,
              delivery_address, delivery_lat, delivery_lng))

        cursor.execute('DELETE FROM cart WHERE user_id = ?',
                       (user['user_id'], ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Order placed successfully!',
            'order_id': order_id
        })

    return render_template('checkout.html', user=user)


@app.route('/orders')
def orders():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
        (user['user_id'], ))
    orders = [dict(row) for row in cursor.fetchall()]

    for order in orders:
        order['products'] = json.loads(order['products'])

    conn.close()

    return render_template('orders.html', orders=orders, user=user)


@app.route('/api/categories')
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT DISTINCT category FROM products WHERE category IS NOT NULL')
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()

    return jsonify(categories)


@app.route('/api/firebase-config')
def firebase_config():
    firebase_api_key = os.environ.get('FIREBASE_API_KEY')

    if not firebase_api_key:
        return jsonify({'enabled': False})

    return jsonify({
        'enabled': True,
        'firebaseConfig': {
            'apiKey': firebase_api_key,
            'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
            'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
            'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID',
                                                ''),
            'appId': os.environ.get('FIREBASE_APP_ID', '')
        },
        'vapidKey': os.environ.get('FIREBASE_VAPID_KEY', '')
    })


@app.route('/api/save-fcm-token', methods=['POST'])
def save_fcm_token():
    user = get_current_user()

    if not user:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    data = request.json
    fcm_token = data.get('token')

    if fcm_token:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fcm_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute(
            'SELECT * FROM fcm_tokens WHERE user_id = ? AND token = ?',
            (user['user_id'], fcm_token))

        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO fcm_tokens (user_id, token) VALUES (?, ?)',
                (user['user_id'], fcm_token))
            conn.commit()

        conn.close()

        return jsonify({'success': True, 'message': 'FCM token saved'})

    return jsonify({'success': False, 'message': 'No token provided'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
