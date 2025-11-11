from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Text, Integer, Float, Boolean, String

db = SQLAlchemy()

class TempUser(db.Model):
    __tablename__ = 'temp_users'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(200), nullable=False)
    full_name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    user_type = db.Column(String(20), default='buyer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(200), nullable=False)
    full_name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    user_type = db.Column(String(20), default='buyer')
    login_status = db.Column(Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    shop_name = db.Column(String(200))
    shop_address = db.Column(Text)
    shop_latitude = db.Column(Float)
    shop_longitude = db.Column(Float)
    shop_city = db.Column(String(100))
    shop_pincode = db.Column(String(10))
    
    fcm_token = db.Column(String(255))
    
    auth_tokens = db.relationship('AuthToken', backref='user', lazy=True, cascade='all, delete-orphan')
    products = db.relationship('Product', backref='seller', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    pickup_items = db.relationship('PickupItem', foreign_keys='PickupItem.user_id', backref='buyer', lazy=True, cascade='all, delete-orphan')
    pickup_seller_items = db.relationship('PickupItem', foreign_keys='PickupItem.seller_id', backref='seller_pickup', lazy=True)
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='user', lazy=True, cascade='all, delete-orphan')
    seller_orders = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    logout_tokens = db.relationship('LogoutToken', backref='user', lazy=True, cascade='all, delete-orphan')

class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(String(200), unique=True, nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(Integer, default=1)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(Integer, primary_key=True)
    product_id = db.Column(String(100), unique=True, nullable=False)
    seller_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    category = db.Column(String(100))
    price = db.Column(Float, nullable=False)
    stock = db.Column(Integer, default=0)
    online_stock = db.Column(Integer, default=0)
    images = db.Column(Text)
    is_visible = db.Column(Integer, default=1)
    expiry_date = db.Column(String(50))
    rating = db.Column(Float, default=0.0)
    rating_count = db.Column(Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cart_items = db.relationship('Cart', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(String(100), db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(Integer, default=1)
    purchase_option = db.Column(String(20), default='delivery')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class PickupItem(db.Model):
    __tablename__ = 'pickup_items'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(String(100), db.ForeignKey('products.product_id'), nullable=False)
    seller_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    quantity = db.Column(Integer, default=1)
    shop_lat = db.Column(Float, nullable=False)
    shop_lng = db.Column(Float, nullable=False)
    shop_name = db.Column(String(200))
    shop_address = db.Column(Text)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(String(100), unique=True, nullable=False)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    products = db.Column(Text, nullable=False)
    total_amount = db.Column(Float, nullable=False)
    delivery_address = db.Column(Text)
    delivery_lat = db.Column(Float)
    delivery_lng = db.Column(Float)
    purchase_option = db.Column(String(50), default='delivery')
    pickup_slot = db.Column(String(100))
    seller_id = db.Column(String(100), db.ForeignKey('users.user_id'))
    status = db.Column(String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Address(db.Model):
    __tablename__ = 'addresses'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    address_line = db.Column(Text, nullable=False)
    city = db.Column(String(100))
    state = db.Column(String(100))
    pincode = db.Column(String(10))
    latitude = db.Column(Float)
    longitude = db.Column(Float)
    is_default = db.Column(Integer, default=0)

class LogoutToken(db.Model):
    __tablename__ = 'logout_tokens'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(Integer, default=0)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(Integer, primary_key=True)
    product_id = db.Column(String(100), db.ForeignKey('products.product_id'), nullable=False)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(Integer, nullable=False)
    comment = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RoutePlan(db.Model):
    __tablename__ = 'route_plans'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    origin_lat = db.Column(Float, nullable=False)
    origin_lng = db.Column(Float, nullable=False)
    destination_lat = db.Column(Float)
    destination_lng = db.Column(Float)
    gemini_request = db.Column(Text)
    gemini_response = db.Column(Text)
    status = db.Column(String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stops = db.relationship('RoutePlanStop', backref='route', lazy=True, cascade='all, delete-orphan')

class RoutePlanStop(db.Model):
    __tablename__ = 'route_plan_stops'
    
    id = db.Column(Integer, primary_key=True)
    route_plan_id = db.Column(Integer, db.ForeignKey('route_plans.id'), nullable=False)
    seller_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(String(100), db.ForeignKey('products.product_id'), nullable=False)
    stop_order = db.Column(Integer, nullable=False)
    shop_lat = db.Column(Float, nullable=False)
    shop_lng = db.Column(Float, nullable=False)
    estimated_arrival = db.Column(String(50))
