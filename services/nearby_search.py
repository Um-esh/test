from models import User, Product
from services.geolocation import haversine_distance

def find_nearby_sellers(product_name, user_lat, user_lng, max_distance_km=10, category=None):
    """
    Find sellers with the product within specified distance
    Returns list of (seller, product, distance) tuples
    """
    query = Product.query.filter(Product.is_visible == 1)
    
    if product_name:
        query = query.filter(Product.name.ilike(f'%{product_name}%'))
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()
    
    results = []
    for product in products:
        seller = User.query.filter_by(user_id=product.seller_id).first()
        if not seller or not seller.shop_latitude or not seller.shop_longitude:
            continue
        
        distance = haversine_distance(
            user_lat, user_lng,
            seller.shop_latitude, seller.shop_longitude
        )
        
        if distance <= max_distance_km:
            results.append({
                'seller': seller,
                'product': product,
                'distance_km': round(distance, 2)
            })
    
    results.sort(key=lambda x: x['distance_km'])
    return results

def filter_search_results(results, min_price=None, max_price=None, min_rating=None, 
                         in_stock_only=True, purchase_option=None):
    """Apply filters to search results"""
    filtered = results
    
    if min_price is not None:
        filtered = [r for r in filtered if r['product'].price >= min_price]
    
    if max_price is not None:
        filtered = [r for r in filtered if r['product'].price <= max_price]
    
    if min_rating is not None:
        filtered = [r for r in filtered if r['product'].rating >= min_rating]
    
    if in_stock_only:
        if purchase_option == 'delivery':
            filtered = [r for r in filtered if r['product'].online_stock > 0]
        else:
            filtered = [r for r in filtered if r['product'].stock > 0]
    
    return filtered
