from models import db, TempUser, LogoutToken
from datetime import datetime
from flask import current_app

def init_db(app):
    with app.app_context():
        db.create_all()

def cleanup_expired_temp_users():
    from app import app
    with app.app_context():
        try:
            TempUser.query.filter(TempUser.expires_at < datetime.utcnow()).delete()
            LogoutToken.query.filter(LogoutToken.expires_at < datetime.utcnow()).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up expired users: {e}")
