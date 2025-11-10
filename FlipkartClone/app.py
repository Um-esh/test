from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import secrets
from datetime import datetime
import math
from apscheduler.schedulers.background import BackgroundScheduler

from models import db, User, Product, Cart, Order, Address, TempUser, AuthToken
from database import init_db, cleanup_expired_temp_users
from auth import create_temp_user, verify_and_move_user, create_auth_token, verify_token, logout_user, create_logout_token, verify_logout_token

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'srms.inventory@gmail.com'
app.config['MAIL_PASSWORD'] = 'ilslkasxuyqcqnke'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'noreply@ecommerce.com')

db.init_app(app)
mail = Mail(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db(app)

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_expired_temp_users, trigger="interval", minutes=5)
scheduler.start()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    token = request.cookies.get('auth_token')
    user_id = request.cookies.get('user_id')

    if token and user_id:
        verified_user_id = verify_token(token)
        if verified_user_id == user_id:
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                return {
                    'id': user.id,
                    'user_id': user.user_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone': user.phone,
                    'user_type': user.user_type,
                    'login_status': user.login_status,
                    'shop_name': user.shop_name,
                    'shop_address': user.shop_address,
                    'shop_latitude': user.shop_latitude,
                    'shop_longitude': user.shop_longitude,
                    'shop_city': user.shop_city,
                    'shop_pincode': user.shop_pincode
                }
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@app.route('/')
def index():
    user = get_current_user()
    mode = request.args.get('mode', 'global')
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    
    query = Product.query.filter_by(is_visible=1)
    
    if mode == 'local' and user_lat is not None and user_lng is not None:
        all_products = query.order_by(Product.created_at.desc()).all()
        nearby_products = []
        
        for product in all_products:
            seller = User.query.filter_by(user_id=product.seller_id).first()
            if seller and seller.shop_latitude is not None and seller.shop_longitude is not None and seller.shop_latitude != 0.0 and seller.shop_longitude != 0.0:
                distance = calculate_distance(user_lat, user_lng, seller.shop_latitude, seller.shop_longitude)
                if distance <= 30:
                    product.distance = round(distance, 1)
                    product.seller_shop_name = seller.shop_name
                    nearby_products.append(product)
        
        products = sorted(nearby_products, key=lambda x: x.distance)
    else:
        products = query.order_by(Product.created_at.desc()).limit(20).all()
        for product in products:
            product.distance = None
            seller = User.query.filter_by(user_id=product.seller_id).first()
            if seller:
                product.seller_shop_name = seller.shop_name
    
    products_data = []
    for product in products:
        product_dict = {
            'id': product.id,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'images': json.loads(product.images) if product.images else [],
            'distance': product.distance if hasattr(product, 'distance') else None,
            'seller_shop_name': product.seller_shop_name if hasattr(product, 'seller_shop_name') else None
        }
        products_data.append(product_dict)
    
    return render_template('index.html', products=products_data, user=user, mode=mode)

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
        user_id = create_temp_user(email, password_hash, full_name, phone, user_type)

        if user_id:
            verification_link = f"{request.host_url}verify/{user_id}"

            try:
                msg = Message('Verify Your Email - Local Trade', recipients=[email])
                msg.html = f'''
                <h2>Welcome to Local Trade!</h2>
                <p>Hi {full_name},</p>
                <p>Thank you for registering. Please verify your email within 15 minutes by clicking the link below:</p>
                <p><a href="{verification_link}" style="background-color: #2874f0; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
                <p>If the button doesn't work, copy and paste this link: {verification_link}</p>
                <p>This link will expire in 15 minutes.</p>
                '''
                mail.send(msg)
                return jsonify({'success': True, 'message': 'Registration successful! Check your email to verify.'})
            except Exception as e:
                return jsonify({'success': True, 'message': 'Registration successful! (Email service not configured)', 'user_id': user_id})
        else:
            return jsonify({'success': False, 'message': 'Email already registered'})

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

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.login_status == 1 and not force_login:
                try:
                    msg = Message('New Login Attempt', recipients=[user.email])
                    msg.html = f'''
                    <h2>New Login Attempt Detected</h2>
                    <p>Hi {user.full_name},</p>
                    <p>Someone is trying to log into your account from a new device/browser.</p>
                    <p>If this was you, please confirm the login in your browser.</p>
                    <p>If this wasn't you, your account may be at risk. Please change your password immediately.</p>
                    '''
                    mail.send(msg)
                except:
                    pass
                
                return jsonify({'success': False, 'message': 'Account already logged in elsewhere', 'already_logged_in': True})
            
            token = create_auth_token(user.user_id)

            response = make_response(jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'user_type': user.user_type
                }
            }))

            response.set_cookie('user_id', user.user_id, max_age=30 * 24 * 60 * 60, httponly=True)
            response.set_cookie('auth_token', token, max_age=30 * 24 * 60 * 60, httponly=True)

            return response
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout_route():
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
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            reset_token = create_logout_token(user.user_id)
            reset_link = f"{request.host_url}reset-password/{reset_token}"
            
            try:
                msg = Message('Password Reset Request', recipients=[email])
                msg.html = f'''
                <h2>Password Reset Request</h2>
                <p>Hi {user.full_name},</p>
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
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                user.password_hash = password_hash
                user.login_status = 0
                
                AuthToken.query.filter_by(user_id=user_id).update({'is_active': 0})
                db.session.commit()
                
                return jsonify({'success': True, 'message': 'Password reset successful! Please login.'})
        
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
    mode = request.args.get('mode', 'global')
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)

    query = Product.query.filter_by(is_visible=1)

    if category:
        query = query.filter_by(category=category)

    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            (Product.name.like(search_filter)) |
            (Product.description.like(search_filter)) |
            (Product.category.like(search_filter))
        )

    if mode == 'local' and user_lat is not None and user_lng is not None:
        all_products = query.order_by(Product.created_at.desc()).all()
        nearby_products = []
        
        for product in all_products:
            seller = User.query.filter_by(user_id=product.seller_id).first()
            if seller and seller.shop_latitude is not None and seller.shop_longitude is not None and seller.shop_latitude != 0.0 and seller.shop_longitude != 0.0:
                distance = calculate_distance(user_lat, user_lng, seller.shop_latitude, seller.shop_longitude)
                if distance <= 30:
                    product.distance = round(distance, 1)
                    product.seller_shop_name = seller.shop_name
                    nearby_products.append(product)
        
        products_list = sorted(nearby_products, key=lambda x: x.distance)
    else:
        products_list = query.order_by(Product.created_at.desc()).all()
        for product in products_list:
            product.distance = None
            seller = User.query.filter_by(user_id=product.seller_id).first()
            if seller:
                product.seller_shop_name = seller.shop_name

    products_data = []
    for product in products_list:
        product_dict = {
            'id': product.id,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'images': json.loads(product.images) if product.images else [],
            'distance': product.distance if hasattr(product, 'distance') else None,
            'seller_shop_name': product.seller_shop_name if hasattr(product, 'seller_shop_name') else None
        }
        products_data.append(product_dict)

    user = get_current_user()
    return render_template('products.html', products=products_data, user=user, mode=mode)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = Product.query.filter_by(product_id=product_id).first()

    if product:
        seller = User.query.filter_by(user_id=product.seller_id).first()
        product_dict = {
            'id': product.id,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'images': json.loads(product.images) if product.images else [],
            'seller_shop_name': seller.shop_name if seller else None,
            'seller_shop_address': seller.shop_address if seller else None,
            'seller_shop_latitude': seller.shop_latitude if seller else None,
            'seller_shop_longitude': seller.shop_longitude if seller else None
        }

        user = get_current_user()
        return render_template('product_detail.html', product=product_dict, user=user)
    else:
        return "Product not found", 404

@app.route('/seller/dashboard')
def seller_dashboard():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return redirect(url_for('login'))

    products = Product.query.filter_by(seller_id=user['user_id']).all()

    products_data = []
    for product in products:
        product_dict = {
            'id': product.id,
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'price': product.price,
            'stock': product.stock,
            'images': json.loads(product.images) if product.images else [],
            'is_visible': product.is_visible,
            'expiry_date': product.expiry_date
        }
        products_data.append(product_dict)

    return render_template('seller_dashboard.html', products=products_data, user=user)

@app.route('/seller/update-shop-location', methods=['POST'])
def update_shop_location():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    shop_name = data.get('shop_name')
    shop_address = data.get('shop_address')
    shop_latitude = data.get('shop_latitude')
    shop_longitude = data.get('shop_longitude')
    shop_city = data.get('shop_city')
    shop_pincode = data.get('shop_pincode')

    if shop_latitude is not None and shop_longitude is not None:
        if shop_latitude == 0.0 and shop_longitude == 0.0:
            return jsonify({'success': False, 'message': 'Invalid coordinates: 0,0 is not a valid shop location. Please enter your actual coordinates.'}), 400
        if not (-90 <= shop_latitude <= 90) or not (-180 <= shop_longitude <= 180):
            return jsonify({'success': False, 'message': 'Invalid coordinates: Latitude must be between -90 and 90, Longitude must be between -180 and 180.'}), 400

    seller = User.query.filter_by(user_id=user['user_id']).first()
    if seller:
        seller.shop_name = shop_name
        seller.shop_address = shop_address
        seller.shop_latitude = shop_latitude
        seller.shop_longitude = shop_longitude
        seller.shop_city = shop_city
        seller.shop_pincode = shop_pincode
        db.session.commit()
        return jsonify({'success': True, 'message': 'Shop location updated successfully'})

    return jsonify({'success': False, 'message': 'User not found'})

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

        product_id = f"PROD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        image_paths = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{product_id}_{secrets.token_hex(4)}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_paths.append(f"/static/uploads/{filename}")

        new_product = Product(
            product_id=product_id,
            seller_id=user['user_id'],
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
            images=json.dumps(image_paths),
            is_visible=int(is_visible),
            expiry_date=expiry_date
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Product added successfully!', 'product_id': product_id})

    return render_template('add_product.html', user=user)

@app.route('/seller/update-product/<product_id>', methods=['POST'])
def update_product(product_id):
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    product = Product.query.filter_by(product_id=product_id, seller_id=user['user_id']).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'Unauthorized or product not found'}), 403

    if 'price' in data:
        product.price = float(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'is_visible' in data:
        product.is_visible = int(data['is_visible'])
    if 'expiry_date' in data:
        product.expiry_date = data['expiry_date']
    
    db.session.commit()

    return jsonify({'success': True, 'message': 'Product updated successfully'})

@app.route('/seller/orders')
def seller_orders():
    user = get_current_user()

    if not user or user['user_type'] != 'seller':
        return redirect(url_for('login'))

    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    seller_orders = []
    
    for order in all_orders:
        products_data = json.loads(order.products)
        seller_products = [p for p in products_data if Product.query.filter_by(product_id=p['product_id'], seller_id=user['user_id']).first()]
        if seller_products:
            order_dict = {
                'order_id': order.order_id,
                'user_id': order.user_id,
                'products': seller_products,
                'total_amount': order.total_amount,
                'delivery_address': order.delivery_address,
                'status': order.status,
                'created_at': order.created_at
            }
            seller_orders.append(order_dict)

    return render_template('seller_orders.html', orders=seller_orders, user=user)

@app.route('/cart')
def cart():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user['user_id']).all()

    cart_data = []
    for cart_item, product in cart_items:
        item_dict = {
            'id': cart_item.id,
            'product_id': cart_item.product_id,
            'quantity': cart_item.quantity,
            'name': product.name,
            'price': product.price,
            'images': json.loads(product.images) if product.images else []
        }
        cart_data.append(item_dict)

    return render_template('cart.html', cart_items=cart_data, user=user)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    user = get_current_user()

    if not user:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    existing = Cart.query.filter_by(user_id=user['user_id'], product_id=product_id).first()

    if existing:
        existing.quantity += quantity
        message = 'Quantity updated in cart!'
    else:
        new_cart_item = Cart(user_id=user['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
        message = 'Added to cart!'

    db.session.commit()

    return jsonify({'success': True, 'message': message})

@app.route('/cart/check/<product_id>')
def check_cart(product_id):
    user = get_current_user()

    if not user:
        return jsonify({'in_cart': False})

    item = Cart.query.filter_by(user_id=user['user_id'], product_id=product_id).first()

    if item:
        return jsonify({'in_cart': True, 'quantity': item.quantity})
    else:
        return jsonify({'in_cart': False})

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    user = get_current_user()

    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user['user_id']).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

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

        cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user['user_id']).all()

        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})

        total_amount = sum(product.price * cart_item.quantity for cart_item, product in cart_items)
        order_id = f"ORD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"

        products_json = json.dumps([{
            'product_id': cart_item.product_id,
            'name': product.name,
            'quantity': cart_item.quantity,
            'price': product.price
        } for cart_item, product in cart_items])

        new_order = Order(
            order_id=order_id,
            user_id=user['user_id'],
            products=products_json,
            total_amount=total_amount,
            delivery_address=delivery_address,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng
        )
        db.session.add(new_order)
        
        Cart.query.filter_by(user_id=user['user_id']).delete()
        
        db.session.commit()

        return jsonify({'success': True, 'message': 'Order placed successfully!', 'order_id': order_id})

    return render_template('checkout.html', user=user)

@app.route('/orders')
def orders():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    orders_list = Order.query.filter_by(user_id=user['user_id']).order_by(Order.created_at.desc()).all()

    orders_data = []
    for order in orders_list:
        order_dict = {
            'order_id': order.order_id,
            'products': json.loads(order.products),
            'total_amount': order.total_amount,
            'delivery_address': order.delivery_address,
            'status': order.status,
            'created_at': order.created_at
        }
        orders_data.append(order_dict)

    return render_template('orders.html', orders=orders_data, user=user)

@app.route('/api/categories')
def get_categories():
    categories = db.session.query(Product.category).filter(Product.category.isnot(None)).distinct().all()
    categories_list = [cat[0] for cat in categories]
    return jsonify(categories_list)

@app.route('/api/nearby-shops')
def nearby_shops():
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    
    if user_lat is None or user_lng is None:
        return jsonify([])
    
    sellers = User.query.filter(User.shop_latitude.isnot(None), User.shop_longitude.isnot(None)).all()
    nearby_shops = []
    
    for seller in sellers:
        if seller.shop_latitude == 0.0 and seller.shop_longitude == 0.0:
            continue
        distance = calculate_distance(user_lat, user_lng, seller.shop_latitude, seller.shop_longitude)
        if distance <= 30:
            shop_dict = {
                'shop_name': seller.shop_name,
                'shop_address': seller.shop_address,
                'latitude': seller.shop_latitude,
                'longitude': seller.shop_longitude,
                'city': seller.shop_city,
                'distance': round(distance, 1)
            }
            nearby_shops.append(shop_dict)
    
    nearby_shops.sort(key=lambda x: x['distance'])
    return jsonify(nearby_shops)

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
            'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
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
        seller = User.query.filter_by(user_id=user['user_id']).first()
        if seller:
            seller.fcm_token = fcm_token
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'FCM token saved'})

    return jsonify({'success': False, 'message': 'No token provided'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
