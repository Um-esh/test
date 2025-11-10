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
    'Beauty & Personal Care', 'Sports & Fitness', 'Books', 'Toys',
    'Automotive', 'Health & Wellness', 'Office Supplies', 'Pet Supplies'
]

CITIES = [
    {'name': 'Bareilly', 'lat': 28.3670, 'lng': 79.4304},
    {'name': 'Mumbai', 'lat': 19.076, 'lng': 72.877},
    {'name': 'Delhi', 'lat': 28.704, 'lng': 77.102},
    {'name': 'Bangalore', 'lat': 12.972, 'lng': 77.594},
    {'name': 'Pune', 'lat': 18.520, 'lng': 73.857},
]

PRODUCTS_CATALOG = [
    {'cat': 'Groceries', 'name': 'Organic Bananas', 'price': 40, 'desc': 'Fresh organic bananas'},
    {'cat': 'Groceries', 'name': 'Whole Wheat Bread', 'price': 45, 'desc': 'Freshly baked bread'},
    {'cat': 'Groceries', 'name': 'Fresh Milk 1L', 'price': 60, 'desc': 'Farm fresh milk'},
    {'cat': 'Groceries', 'name': 'Basmati Rice 5kg', 'price': 450, 'desc': 'Premium basmati rice'},
    {'cat': 'Groceries', 'name': 'Organic Eggs 12pcs', 'price': 90, 'desc': 'Cage-free eggs'},
    {'cat': 'Groceries', 'name': 'Mixed Vegetables', 'price': 80, 'desc': 'Fresh seasonal vegetables'},
    {'cat': 'Groceries', 'name': 'Greek Yogurt', 'price': 75, 'desc': 'Creamy yogurt'},
    {'cat': 'Groceries', 'name': 'Olive Oil 500ml', 'price': 350, 'desc': 'Extra virgin'},
    {'cat': 'Groceries', 'name': 'Tomatoes 1kg', 'price': 30, 'desc': 'Fresh red tomatoes'},
    {'cat': 'Groceries', 'name': 'Onions 1kg', 'price': 25, 'desc': 'Quality onions'},
    {'cat': 'Groceries', 'name': 'Potatoes 1kg', 'price': 20, 'desc': 'Fresh potatoes'},
    {'cat': 'Groceries', 'name': 'Green Chili', 'price': 40, 'desc': 'Spicy green chili'},
    {'cat': 'Groceries', 'name': 'Ginger 250g', 'price': 60, 'desc': 'Fresh ginger'},
    {'cat': 'Groceries', 'name': 'Garlic 250g', 'price': 50, 'desc': 'Quality garlic'},
    {'cat': 'Groceries', 'name': 'Coriander Leaves', 'price': 15, 'desc': 'Fresh coriander'},
    {'cat': 'Groceries', 'name': 'Mint Leaves', 'price': 10, 'desc': 'Fresh mint'},
    {'cat': 'Groceries', 'name': 'Apples 1kg', 'price': 120, 'desc': 'Kashmiri apples'},
    {'cat': 'Groceries', 'name': 'Oranges 1kg', 'price': 60, 'desc': 'Juicy oranges'},
    {'cat': 'Groceries', 'name': 'Mangoes 1kg', 'price': 150, 'desc': 'Alphonso mangoes'},
    {'cat': 'Groceries', 'name': 'Grapes 500g', 'price': 70, 'desc': 'Seedless grapes'},
    {'cat': 'Electronics', 'name': 'Wireless Mouse', 'price': 599, 'desc': 'Ergonomic mouse'},
    {'cat': 'Electronics', 'name': 'Bluetooth Headphones', 'price': 1499, 'desc': 'Noise cancellation'},
    {'cat': 'Electronics', 'name': 'Phone Charger', 'price': 299, 'desc': 'Fast charging USB-C'},
    {'cat': 'Electronics', 'name': 'Laptop Stand', 'price': 899, 'desc': 'Adjustable stand'},
    {'cat': 'Electronics', 'name': 'USB Hub', 'price': 699, 'desc': '7-port USB 3.0'},
    {'cat': 'Electronics', 'name': 'Webcam HD', 'price': 2499, 'desc': '1080p webcam'},
    {'cat': 'Electronics', 'name': 'Keyboard Wireless', 'price': 1299, 'desc': 'Mechanical keyboard'},
    {'cat': 'Electronics', 'name': 'LED Monitor 24inch', 'price': 8999, 'desc': 'Full HD display'},
    {'cat': 'Electronics', 'name': 'Power Bank 10000mAh', 'price': 999, 'desc': 'Fast charging'},
    {'cat': 'Electronics', 'name': 'USB Cable 3pack', 'price': 299, 'desc': 'Durable cables'},
    {'cat': 'Electronics', 'name': 'Phone Stand', 'price': 199, 'desc': 'Adjustable holder'},
    {'cat': 'Electronics', 'name': 'Earbuds TWS', 'price': 1999, 'desc': 'True wireless'},
    {'cat': 'Electronics', 'name': 'Smart Watch', 'price': 2999, 'desc': 'Fitness tracker'},
    {'cat': 'Electronics', 'name': 'Tablet 10inch', 'price': 12999, 'desc': 'Android tablet'},
    {'cat': 'Fashion', 'name': 'Cotton T-Shirt', 'price': 399, 'desc': '100% cotton'},
    {'cat': 'Fashion', 'name': 'Denim Jeans', 'price': 1299, 'desc': 'Classic fit'},
    {'cat': 'Fashion', 'name': 'Running Shoes', 'price': 2499, 'desc': 'Lightweight'},
    {'cat': 'Fashion', 'name': 'Leather Wallet', 'price': 799, 'desc': 'Genuine leather'},
    {'cat': 'Fashion', 'name': 'Sunglasses', 'price': 599, 'desc': 'UV protection'},
    {'cat': 'Fashion', 'name': 'Winter Jacket', 'price': 3499, 'desc': 'Warm jacket'},
    {'cat': 'Fashion', 'name': 'Formal Shirt', 'price': 899, 'desc': 'Office wear'},
    {'cat': 'Fashion', 'name': 'Sports Shoes', 'price': 1899, 'desc': 'Athletic shoes'},
    {'cat': 'Fashion', 'name': 'Casual Sneakers', 'price': 1599, 'desc': 'Daily wear'},
    {'cat': 'Fashion', 'name': 'Belt Leather', 'price': 499, 'desc': 'Formal belt'},
    {'cat': 'Fashion', 'name': 'Cap Baseball', 'price': 299, 'desc': 'Sports cap'},
    {'cat': 'Fashion', 'name': 'Socks Pack of 5', 'price': 249, 'desc': 'Cotton socks'},
    {'cat': 'Home & Kitchen', 'name': 'Cookware Set', 'price': 2999, 'desc': '5-piece non-stick'},
    {'cat': 'Home & Kitchen', 'name': 'Mixer Grinder', 'price': 3499, 'desc': '750W 3 jars'},
    {'cat': 'Home & Kitchen', 'name': 'Bed Sheet Set', 'price': 1299, 'desc': 'Cotton bedsheet'},
    {'cat': 'Home & Kitchen', 'name': 'Table Lamp', 'price': 699, 'desc': 'LED lamp'},
    {'cat': 'Home & Kitchen', 'name': 'Wall Clock', 'price': 499, 'desc': 'Silent clock'},
    {'cat': 'Home & Kitchen', 'name': 'Dinner Set 24pc', 'price': 1999, 'desc': 'Ceramic set'},
    {'cat': 'Home & Kitchen', 'name': 'Pressure Cooker 5L', 'price': 1599, 'desc': 'Aluminum cooker'},
    {'cat': 'Home & Kitchen', 'name': 'Water Purifier', 'price': 8999, 'desc': 'RO purifier'},
    {'cat': 'Beauty & Personal Care', 'name': 'Face Wash', 'price': 249, 'desc': 'For all skin types'},
    {'cat': 'Beauty & Personal Care', 'name': 'Shampoo 200ml', 'price': 299, 'desc': 'Anti-dandruff'},
    {'cat': 'Beauty & Personal Care', 'name': 'Body Lotion', 'price': 349, 'desc': 'Moisturizing'},
    {'cat': 'Beauty & Personal Care', 'name': 'Perfume EDT', 'price': 999, 'desc': 'Long-lasting'},
    {'cat': 'Beauty & Personal Care', 'name': 'Hair Oil 200ml', 'price': 199, 'desc': 'Herbal oil'},
    {'cat': 'Beauty & Personal Care', 'name': 'Face Cream', 'price': 399, 'desc': 'Day cream'},
    {'cat': 'Beauty & Personal Care', 'name': 'Soap Pack of 3', 'price': 150, 'desc': 'Herbal soap'},
    {'cat': 'Beauty & Personal Care', 'name': 'Toothpaste 200g', 'price': 120, 'desc': 'Dental care'},
    {'cat': 'Sports & Fitness', 'name': 'Yoga Mat', 'price': 599, 'desc': 'Anti-slip mat'},
    {'cat': 'Sports & Fitness', 'name': 'Dumbbells 5kg pair', 'price': 899, 'desc': 'Rubber-coated'},
    {'cat': 'Sports & Fitness', 'name': 'Resistance Bands', 'price': 399, 'desc': 'Set of 3'},
    {'cat': 'Sports & Fitness', 'name': 'Water Bottle 1L', 'price': 299, 'desc': 'Insulated'},
    {'cat': 'Sports & Fitness', 'name': 'Skipping Rope', 'price': 199, 'desc': 'Adjustable'},
    {'cat': 'Sports & Fitness', 'name': 'Gym Bag', 'price': 899, 'desc': 'Sports bag'},
    {'cat': 'Sports & Fitness', 'name': 'Cricket Bat', 'price': 1999, 'desc': 'Willow bat'},
    {'cat': 'Sports & Fitness', 'name': 'Badminton Racket', 'price': 1299, 'desc': 'Lightweight'},
    {'cat': 'Books', 'name': 'Fiction Novel', 'price': 299, 'desc': 'Bestseller'},
    {'cat': 'Books', 'name': 'Self Help Book', 'price': 349, 'desc': 'Motivational'},
    {'cat': 'Books', 'name': 'Cookbook', 'price': 399, 'desc': 'Indian recipes'},
    {'cat': 'Books', 'name': 'Kids Story Book', 'price': 199, 'desc': 'Illustrated'},
    {'cat': 'Books', 'name': 'Dictionary', 'price': 449, 'desc': 'English-Hindi'},
    {'cat': 'Books', 'name': 'Notebook Set', 'price': 249, 'desc': 'Pack of 5'},
    {'cat': 'Toys', 'name': 'Building Blocks', 'price': 599, 'desc': '100 pieces'},
    {'cat': 'Toys', 'name': 'Remote Car', 'price': 899, 'desc': 'RC car'},
    {'cat': 'Toys', 'name': 'Puzzle Game', 'price': 399, 'desc': '1000 pieces'},
    {'cat': 'Toys', 'name': 'Soft Teddy Bear', 'price': 499, 'desc': 'Plush toy'},
    {'cat': 'Toys', 'name': 'Board Game', 'price': 699, 'desc': 'Family game'},
    {'cat': 'Toys', 'name': 'Action Figure', 'price': 799, 'desc': 'Superhero'},
    {'cat': 'Automotive', 'name': 'Car Phone Holder', 'price': 299, 'desc': 'Dashboard mount'},
    {'cat': 'Automotive', 'name': 'Car Vacuum Cleaner', 'price': 1299, 'desc': 'Portable'},
    {'cat': 'Automotive', 'name': 'Tire Pressure Gauge', 'price': 199, 'desc': 'Digital'},
    {'cat': 'Automotive', 'name': 'Car Perfume', 'price': 149, 'desc': 'Long-lasting'},
    {'cat': 'Automotive', 'name': 'Jump Starter', 'price': 2999, 'desc': 'Emergency kit'},
    {'cat': 'Health & Wellness', 'name': 'Vitamin C Tablets', 'price': 299, 'desc': '60 tablets'},
    {'cat': 'Health & Wellness', 'name': 'Protein Powder', 'price': 1999, 'desc': '1kg pack'},
    {'cat': 'Health & Wellness', 'name': 'First Aid Kit', 'price': 599, 'desc': 'Complete kit'},
    {'cat': 'Health & Wellness', 'name': 'Digital Thermometer', 'price': 199, 'desc': 'Infrared'},
    {'cat': 'Health & Wellness', 'name': 'Blood Pressure Monitor', 'price': 1499, 'desc': 'Digital'},
    {'cat': 'Office Supplies', 'name': 'Pen Set 10pcs', 'price': 149, 'desc': 'Ball pens'},
    {'cat': 'Office Supplies', 'name': 'A4 Paper 500 sheets', 'price': 299, 'desc': 'Printing paper'},
    {'cat': 'Office Supplies', 'name': 'Stapler', 'price': 199, 'desc': 'Heavy duty'},
    {'cat': 'Office Supplies', 'name': 'File Folders 10pc', 'price': 249, 'desc': 'Document folders'},
    {'cat': 'Office Supplies', 'name': 'Desk Organizer', 'price': 599, 'desc': 'Multi-compartment'},
    {'cat': 'Pet Supplies', 'name': 'Dog Food 3kg', 'price': 899, 'desc': 'Premium food'},
    {'cat': 'Pet Supplies', 'name': 'Cat Litter 5kg', 'price': 499, 'desc': 'Odor control'},
    {'cat': 'Pet Supplies', 'name': 'Pet Bowl Set', 'price': 299, 'desc': 'Stainless steel'},
    {'cat': 'Pet Supplies', 'name': 'Dog Collar', 'price': 249, 'desc': 'Adjustable'},
    {'cat': 'Pet Supplies', 'name': 'Pet Toy Ball', 'price': 149, 'desc': 'Rubber ball'},
]

SHOP_NAMES = [
    'Fresh Mart', 'Quick Stop', 'City Store', 'Smart Shop', 'Easy Buy',
    'Metro Bazaar', 'Corner Shop', 'Daily Needs', 'Express Store', 'Local Market',
    'Super Save', 'Prime Retail', 'Best Buy Store', 'Value Shop', 'Mega Mart',
    'Happy Store', 'Top Shop', 'Quality Bazaar', 'Trade Point', 'Shop Hub'
]

REVIEWS_COMMENTS = {
    5: ['Excellent product!', 'Highly recommended!', 'Best purchase ever!', 'Amazing quality!'],
    4: ['Very good', 'Worth the money', 'Good quality', 'Happy with purchase'],
    3: ['Decent product', 'Okay for the price', 'Average quality'],
    2: ['Not as expected', 'Could be better', 'Disappointed'],
    1: ['Poor quality', 'Waste of money', 'Very disappointed']
}

def generate_nearby_coordinates(base_lat, base_lng, radius_km=5):
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
        
        print("Creating 15 sellers (exactly 3 from Bareilly, UP)...")
        sellers = []
        seller_counter = 1
        
        for i in range(3):
            city = CITIES[0]
            shop_lat, shop_lng = generate_nearby_coordinates(city['lat'], city['lng'], radius_km=8)
            seller_id = f"SELLER{seller_counter:03d}"
            
            seller = User(
                user_id=seller_id,
                email=f"seller{seller_counter}@buddyshop.com",
                password_hash=generate_password_hash('seller123'),
                full_name=f"Seller {seller_counter}",
                phone=f"98765{random.randint(10000, 99999)}",
                user_type='seller',
                login_status=0,
                shop_name=f"{random.choice(SHOP_NAMES)} - {city['name']}",
                shop_address=f"{random.randint(1, 999)} Civil Lines, {city['name']}, Uttar Pradesh",
                shop_latitude=shop_lat,
                shop_longitude=shop_lng,
                shop_city=city['name'],
                shop_pincode=f"2430{random.randint(10, 99)}"
            )
            db.session.add(seller)
            sellers.append(seller)
            seller_counter += 1
        
        for city_idx in range(1, len(CITIES)):
            city = CITIES[city_idx]
            sellers_in_city = 3
            
            for shop_idx in range(sellers_in_city):
                shop_lat, shop_lng = generate_nearby_coordinates(city['lat'], city['lng'], radius_km=10)
                seller_id = f"SELLER{seller_counter:03d}"
                
                seller = User(
                    user_id=seller_id,
                    email=f"seller{seller_counter}@buddyshop.com",
                    password_hash=generate_password_hash('seller123'),
                    full_name=f"Seller {seller_counter}",
                    phone=f"98765{random.randint(10000, 99999)}",
                    user_type='seller',
                    login_status=0,
                    shop_name=f"{random.choice(SHOP_NAMES)} - {city['name']}",
                    shop_address=f"{random.randint(1, 999)} MG Road, {city['name']}",
                    shop_latitude=shop_lat,
                    shop_longitude=shop_lng,
                    shop_city=city['name'],
                    shop_pincode=f"{random.randint(100000, 999999)}"
                )
                db.session.add(seller)
                sellers.append(seller)
                seller_counter += 1
        
        db.session.commit()
        print(f"Created {len(sellers)} sellers")
        
        print("Creating ~1000 products...")
        products = []
        product_counter = 1
        
        while product_counter <= 1000:
            seller = random.choice(sellers)
            prod_data = random.choice(PRODUCTS_CATALOG)
            
            product_id = f"PROD{product_counter:04d}"
            total_stock = random.randint(10, 200)
            online_stock = random.randint(int(total_stock * 0.3), total_stock)
            
            price_variation = random.randint(-30, 50)
            final_price = max(prod_data['price'] + price_variation, 10)
            
            product = Product(
                product_id=product_id,
                seller_id=seller.user_id,
                name=prod_data['name'],
                description=prod_data['desc'],
                category=prod_data['cat'],
                price=final_price,
                stock=total_stock,
                online_stock=online_stock,
                images=json.dumps([f"https://via.placeholder.com/500x500?text={prod_data['name'].replace(' ', '+')}"]),
                is_visible=1,
                rating=0.0,
                rating_count=0
            )
            db.session.add(product)
            products.append(product)
            product_counter += 1
            
            if product_counter % 100 == 0:
                db.session.commit()
                print(f"Created {product_counter} products...")
        
        db.session.commit()
        print(f"Created {len(products)} products")
        
        print("Creating sample buyers...")
        buyers = []
        for i in range(20):
            buyer_id = f"BUYER{i+1:03d}"
            buyer = User(
                user_id=buyer_id,
                email=f"buyer{i+1}@buddyshop.com",
                password_hash=generate_password_hash('buyer123'),
                full_name=f"Buyer {i+1}",
                phone=f"98765{random.randint(10000, 99999)}",
                user_type='buyer',
                login_status=0
            )
            db.session.add(buyer)
            buyers.append(buyer)
        
        db.session.commit()
        print(f"Created {len(buyers)} buyers")
        
        print("Creating reviews for products...")
        review_count = 0
        for product in random.sample(products, min(500, len(products))):
            num_reviews = random.randint(1, 6)
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
            
            if review_count % 100 == 0:
                db.session.commit()
        
        db.session.commit()
        print(f"Created {review_count} reviews")
        
        print("\n=== Seed Data Created Successfully! ===")
        print(f"Sellers: {len(sellers)} (3 from Bareilly, UP)")
        print(f"Products: {len(products)}")
        print(f"Buyers: {len(buyers)}")
        print(f"Reviews: {review_count}")
        print("\nTest Accounts:")
        print("Seller: seller1@buddyshop.com / seller123 (Bareilly)")
        print("Seller: seller2@buddyshop.com / seller123 (Bareilly)")
        print("Buyer: buyer1@buddyshop.com / buyer123")

if __name__ == '__main__':
    seed_data()
