import secrets
import hashlib
from datetime import datetime, timedelta
from models import db, User, TempUser, AuthToken, LogoutToken

def generate_user_id(email):
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    hash_obj = hashlib.md5(email.encode())
    return f"USER_{timestamp}_{hash_obj.hexdigest()[:8]}"

def generate_auth_token(user_id, login_time):
    random_part = secrets.token_urlsafe(32)
    timestamp = login_time.strftime('%Y%m%d%H%M%S')
    combined = f"{user_id}_{timestamp}_{random_part}"
    return hashlib.sha256(combined.encode()).hexdigest()

def create_temp_user(email, password_hash, full_name, phone, user_type):
    user_id = generate_user_id(email)
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    try:
        temp_user = TempUser(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            user_type=user_type,
            expires_at=expires_at
        )
        db.session.add(temp_user)
        db.session.commit()
        return user_id
    except Exception as e:
        db.session.rollback()
        print(f"Error creating temp user: {e}")
        return None

def verify_and_move_user(user_id):
    try:
        temp_user = TempUser.query.filter_by(user_id=user_id).filter(
            TempUser.expires_at > datetime.utcnow()
        ).first()
        
        if temp_user:
            new_user = User(
                user_id=temp_user.user_id,
                email=temp_user.email,
                password_hash=temp_user.password_hash,
                full_name=temp_user.full_name,
                phone=temp_user.phone,
                user_type=temp_user.user_type
            )
            db.session.add(new_user)
            db.session.delete(temp_user)
            db.session.commit()
            return True
        
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error verifying user: {e}")
        return False

def create_auth_token(user_id):
    login_time = datetime.utcnow()
    token = generate_auth_token(user_id, login_time)
    
    try:
        auth_token = AuthToken(
            user_id=user_id,
            token=token,
            login_time=login_time
        )
        db.session.add(auth_token)
        
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.login_status = 1
        
        db.session.commit()
        return token
    except Exception as e:
        db.session.rollback()
        print(f"Error creating auth token: {e}")
        return None

def verify_token(token):
    try:
        auth_token = AuthToken.query.filter_by(token=token, is_active=1).first()
        return auth_token.user_id if auth_token else None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def create_logout_token(user_id):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    try:
        logout_token = LogoutToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(logout_token)
        db.session.commit()
        return token
    except Exception as e:
        db.session.rollback()
        print(f"Error creating logout token: {e}")
        return None

def verify_logout_token(token):
    try:
        logout_token = LogoutToken.query.filter_by(token=token, used=0).filter(
            LogoutToken.expires_at > datetime.utcnow()
        ).first()
        
        if logout_token:
            logout_token.used = 1
            db.session.commit()
            return logout_token.user_id
        
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error verifying logout token: {e}")
        return None

def logout_user(user_id):
    try:
        AuthToken.query.filter_by(user_id=user_id).update({'is_active': 0})
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.login_status = 0
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging out user: {e}")
