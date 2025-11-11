from models import db, Review, Product
from sqlalchemy import func

def add_review(product_id, user_id, rating, comment=''):
    """Add a product review and update product rating"""
    existing_review = Review.query.filter_by(
        product_id=product_id, 
        user_id=user_id
    ).first()
    
    if existing_review:
        existing_review.rating = rating
        existing_review.comment = comment
    else:
        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
    
    update_product_rating(product_id)
    db.session.commit()
    return True

def update_product_rating(product_id):
    """Recalculate and update product's average rating"""
    result = db.session.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.product_id == product_id).first()
    
    avg_rating, count = result
    
    product = Product.query.filter_by(product_id=product_id).first()
    if product:
        product.rating = round(avg_rating, 1) if avg_rating else 0.0
        product.rating_count = count if count else 0
        db.session.commit()

def get_product_reviews(product_id, limit=10):
    """Get reviews for a product"""
    return Review.query.filter_by(product_id=product_id).order_by(
        Review.created_at.desc()
    ).limit(limit).all()
