from models import db, Product

def check_stock_availability(product_id, quantity, purchase_option='delivery'):
    """
    Check if product has sufficient stock for the purchase option
    purchase_option: 'delivery', 'pickup', 'in-store'
    """
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return False, "Product not found"
    
    if purchase_option == 'delivery':
        if product.online_stock >= quantity:
            return True, "Available for delivery"
        return False, f"Only {product.online_stock} available for delivery"
    
    elif purchase_option in ['pickup', 'in-store']:
        if product.stock >= quantity:
            return True, f"Available for {purchase_option}"
        return False, f"Only {product.stock} available in store"
    
    return False, "Invalid purchase option"

def decrement_stock(product_id, quantity, purchase_option='delivery'):
    """Decrement stock based on purchase option"""
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return False
    
    if purchase_option == 'delivery':
        if product.online_stock >= quantity:
            product.online_stock -= quantity
            product.stock -= quantity
            db.session.commit()
            return True
    else:
        if product.stock >= quantity:
            product.stock -= quantity
            db.session.commit()
            return True
    
    return False

def update_product_inventory(product_id, total_stock, online_stock):
    """Update product inventory levels"""
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return False
    
    if online_stock > total_stock:
        online_stock = total_stock
    
    product.stock = total_stock
    product.online_stock = online_stock
    db.session.commit()
    return True
