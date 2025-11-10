import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Product, Review
from werkzeug.security import generate_password_hash
import random
import secrets
import json

CATEGORIES = [
    'Groceries', 'Electronics', 'Fashion', 'Home & Kitchen', 
    'Beauty & Personal Care', 'Sports & Fitness', 'Books', 'Toys'
]

CITIES = [
    {'name': 'Mumbai', 'lat': 19.076, 'lng': 72.877},
    {'name': 'Delhi', 'lat': 28.704, 'lng': 77.102},
    {'name': 'Bangalore', 'lat': 12.972, 'lng': 77.594},
    {'name': 'Pune', 'lat': 18.520, 'lng': 73.857},
    {'name': 'Hyderabad', 'lat': 17.385, 'lng': 78.487}
]

PRODUCTS = {
    'Groceries': [
        {'name': 'Organic Bananas', 'price': 40, 'desc': 'Fresh organic bananas, rich in potassium', 'img': 'https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=500&h=500&fit=crop'},
        {'name': 'Whole Wheat Bread', 'price': 45, 'desc': 'Freshly baked whole wheat bread', 'img': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&h=500&fit=crop'},
        {'name': 'Fresh Milk (1L)', 'price': 60, 'desc': 'Farm fresh full cream milk', 'img': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&h=500&fit=crop'},
        {'name': 'Basmati Rice (5kg)', 'price': 450, 'desc': 'Premium quality basmati rice', 'img': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&h=500&fit=crop'},
        {'name': 'Organic Eggs (12pcs)', 'price': 90, 'desc': 'Cage-free organic eggs', 'img': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=500&h=500&fit=crop'},
        {'name': 'Mixed Vegetables', 'price': 80, 'desc': 'Fresh seasonal vegetables', 'img': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&h=500&fit=crop'},
        {'name': 'Greek Yogurt', 'price': 75, 'desc': 'Creamy Greek yogurt', 'img': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&h=500&fit=crop'},
        {'name': 'Olive Oil (500ml)', 'price': 350, 'desc': 'Extra virgin olive oil', 'img': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&h=500&fit=crop'},
    ],
    'Electronics': [
        {'name': 'Wireless Mouse', 'price': 599, 'desc': 'Ergonomic wireless mouse with USB receiver', 'img': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&h=500&fit=crop'},
        {'name': 'Bluetooth Headphones', 'price': 1499, 'desc': 'Over-ear wireless headphones with noise cancellation', 'img': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop'},
        {'name': 'Phone Charger', 'price': 299, 'desc': 'Fast charging USB-C charger', 'img': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500&h=500&fit=crop'},
        {'name': 'Laptop Stand', 'price': 899, 'desc': 'Adjustable aluminum laptop stand', 'img': 'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500&h=500&fit=crop'},
        {'name': 'USB Hub', 'price': 699, 'desc': '7-port USB 3.0 hub', 'img': 'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500&h=500&fit=crop'},
        {'name': 'Webcam HD', 'price': 2499, 'desc': '1080p HD webcam with microphone', 'img': 'https://images.unsplash.com/photo-1614624532983-4ce03382d63d?w=500&h=500&fit=crop'},
    ],
    'Fashion': [
        {'name': 'Cotton T-Shirt', 'price': 399, 'desc': 'Comfortable 100% cotton t-shirt', 'img': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=500&fit=crop'},
        {'name': 'Denim Jeans', 'price': 1299, 'desc': 'Classic fit denim jeans', 'img': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&h=500&fit=crop'},
        {'name': 'Running Shoes', 'price': 2499, 'desc': 'Lightweight running shoes', 'img': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=500&fit=crop'},
        {'name': 'Leather Wallet', 'price': 799, 'desc': 'Genuine leather bifold wallet', 'img': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=500&h=500&fit=crop'},
        {'name': 'Sunglasses', 'price': 599, 'desc': 'UV protection sunglasses', 'img': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&h=500&fit=crop'},
        {'name': 'Winter Jacket', 'price': 3499, 'desc': 'Warm winter jacket with hood', 'img': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&h=500&fit=crop'},
    ],
    'Home & Kitchen': [
        {'name': 'Non-Stick Cookware Set', 'price': 2999, 'desc': '5-piece non-stick cookware set', 'img': 'https://images.unsplash.com/photo-1604335399105-a0c585fd81a1?w=500&h=500&fit=crop'},
        {'name': 'Mixer Grinder', 'price': 3499, 'desc': '750W mixer grinder with 3 jars', 'img': 'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=500&h=500&fit=crop'},
        {'name': 'Bed Sheet Set', 'price': 1299, 'desc': 'Premium cotton bed sheet set', 'img': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500&h=500&fit=crop'},
        {'name': 'Table Lamp', 'price': 699, 'desc': 'LED table lamp with dimmer', 'img': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&h=500&fit=crop'},
        {'name': 'Wall Clock', 'price': 499, 'desc': 'Silent wall clock', 'img': 'https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=500&h=500&fit=crop'},
    ],
    'Beauty & Personal Care': [
        {'name': 'Face Wash', 'price': 249, 'desc': 'Gentle face wash for all skin types', 'img': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&h=500&fit=crop'},
        {'name': 'Shampoo (200ml)', 'price': 299, 'desc': 'Anti-dandruff shampoo', 'img': 'https://images.unsplash.com/photo-1631730486572-226d1f595b68?w=500&h=500&fit=crop'},
        {'name': 'Body Lotion', 'price': 349, 'desc': 'Moisturizing body lotion', 'img': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&h=500&fit=crop'},
        {'name': 'Perfume', 'price': 999, 'desc': 'Long-lasting EDT perfume', 'img': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=500&h=500&fit=crop'},
    ],
    'Sports & Fitness': [
        {'name': 'Yoga Mat', 'price': 599, 'desc': 'Anti-slip yoga mat with carry bag', 'img': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&h=500&fit=crop'},
        {'name': 'Dumbbells (5kg pair)', 'price': 899, 'desc': 'Rubber-coated dumbbells', 'img': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500&h=500&fit=crop'},
        {'name': 'Resistance Bands', 'price': 399, 'desc': 'Set of 3 resistance bands', 'img': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500&h=500&fit=crop'},
        {'name': 'Water Bottle', 'price': 299, 'desc': '1L insulated water bottle', 'img': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&h=500&fit=crop'},
    ]
}

SHOP_NAMES = [
    'Fresh Mart', 'Quick Stop', 'City Store', 'Smart Shop', 'Easy Buy',
    'Metro Bazaar', 'Corner Shop', 'Daily Needs', 'Express Store', 'Local Market',
    'Super Save', 'Prime Retail', 'Best Buy Store', 'Value Shop', 'Mega Mart'
]

REVIEWS_COMMENTS = {
    5: ['Excellent product!', 'Highly recommended!', 'Best purchase ever!', 'Amazing quality!'],
    4: ['Very good', 'Worth the money', 'Good quality', 'Happy with purchase'],
    3: ['Decent product', 'Okay for the price', 'Average quality'],
    2: ['Not as expected', 'Could be better', 'Disappointed'],
    1: ['Poor quality', 'Waste of money', 'Very disappointed']
}

def generate_nearby_coordinates(base_lat, base_lng, radius_km=5):
    """Generate coordinates within radius"""
    offset_lat = (random.random() - 0.5) * (radius_km / 111.0) * 2
    offset_lng = (random.random() - 0.5) * (radius_km / (111.0 * 0.9)) * 2
    return base_lat + offset_lat, base_lng + offset_lng

def seed_data():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Clearing existing data...")
        Review.query.delete()
        Product.query.delete()
        User.query.filter_by(user_type='seller').delete()
        User.query.filter_by(user_type='buyer').delete()
        db.session.commit()
        
        print("Creating sellers...")
        sellers = []
        for idx, city in enumerate(CITIES):
            for shop_idx in range(3):
                shop_lat, shop_lng = generate_nearby_coordinates(city['lat'], city['lng'], radius_km=8)
                seller_id = f"SELLER{idx+1}{shop_idx+1}"
                
                seller = User(
                    user_id=seller_id,
                    email=f"seller{idx+1}{shop_idx+1}@buddyshop.com",
                    password_hash=generate_password_hash('seller123'),
                    full_name=f"Seller {idx+1}{shop_idx+1}",
                    phone=f"98765{random.randint(10000, 99999)}",
                    user_type='seller',
                    login_status=1,
                    shop_name=f"{random.choice(SHOP_NAMES)} - {city['name']}",
                    shop_address=f"{random.randint(1, 999)} MG Road, {city['name']}",
                    shop_latitude=shop_lat,
                    shop_longitude=shop_lng,
                    shop_city=city['name'],
                    shop_pincode=f"{random.randint(100000, 999999)}"
                )
                db.session.add(seller)
                sellers.append(seller)
        
        db.session.commit()
        print(f"Created {len(sellers)} sellers")
        
        print("Creating buyers...")
        buyers = []
        for i in range(10):
            buyer_id = f"BUYER{i+1}"
            buyer = User(
                user_id=buyer_id,
                email=f"buyer{i+1}@buddyshop.com",
                password_hash=generate_password_hash('buyer123'),
                full_name=f"Buyer {i+1}",
                phone=f"98765{random.randint(10000, 99999)}",
                user_type='buyer',
                login_status=1
            )
            db.session.add(buyer)
            buyers.append(buyer)
        
        db.session.commit()
        print(f"Created {len(buyers)} buyers")
        
        print("Creating products...")
        products = []
        product_counter = 1
        
        for seller in sellers:
            num_products = random.randint(5, 12)
            seller_categories = random.sample(list(PRODUCTS.keys()), min(3, len(PRODUCTS)))
            
            for category in seller_categories:
                category_products = random.sample(PRODUCTS[category], min(4, len(PRODUCTS[category])))
                
                for prod_data in category_products:
                    product_id = f"PROD{product_counter:04d}"
                    total_stock = random.randint(20, 100)
                    online_stock = random.randint(int(total_stock * 0.5), total_stock)
                    
                    product = Product(
                        product_id=product_id,
                        seller_id=seller.user_id,
                        name=prod_data['name'],
                        description=prod_data['desc'],
                        category=category,
                        price=prod_data['price'] + random.randint(-50, 50),
                        stock=total_stock,
                        online_stock=online_stock,
                        images=json.dumps([prod_data['img']]),
                        is_visible=1,
                        rating=0.0,
                        rating_count=0
                    )
                    db.session.add(product)
                    products.append(product)
                    product_counter += 1
                    
                    if product_counter > num_products:
                        break
        
        db.session.commit()
        print(f"Created {len(products)} products")
        
        print("Creating reviews...")
        review_count = 0
        for product in products:
            num_reviews = random.randint(2, 8)
            reviewers = random.sample(buyers, min(num_reviews, len(buyers)))
            
            total_rating = 0
            for reviewer in reviewers:
                rating = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
                comment = random.choice(REVIEWS_COMMENTS[rating])
                
                review = Review(
                    product_id=product.product_id,
                    user_id=reviewer.user_id,
                    rating=rating,
                    comment=comment
                )
                db.session.add(review)
                total_rating += rating
                review_count += 1
            
            if num_reviews > 0:
                product.rating = round(total_rating / num_reviews, 1)
                product.rating_count = num_reviews
        
        db.session.commit()
        print(f"Created {review_count} reviews")
        
        print("\n=== Sample Data Created Successfully! ===")
        print(f"Sellers: {len(sellers)}")
        print(f"Buyers: {len(buyers)}")
        print(f"Products: {len(products)}")
        print(f"Reviews: {review_count}")
        print("\nTest Accounts:")
        print("Seller: seller11@buddyshop.com / seller123")
        print("Buyer: buyer1@buddyshop.com / buyer123")

if __name__ == '__main__':
    seed_data()
