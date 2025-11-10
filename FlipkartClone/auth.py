import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta
from database import get_db_connection

def generate_user_id(email):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    hash_obj = hashlib.md5(email.encode())
    return f"USER_{timestamp}_{hash_obj.hexdigest()[:8]}"

def generate_auth_token(user_id, login_time):
    random_part = secrets.token_urlsafe(32)
    timestamp = login_time.strftime('%Y%m%d%H%M%S')
    combined = f"{user_id}_{timestamp}_{random_part}"
    return hashlib.sha256(combined.encode()).hexdigest()

def create_temp_user(email, password_hash, full_name, phone, user_type):
    user_id = generate_user_id(email)
    expires_at = datetime.now() + timedelta(minutes=15)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO temp_users (user_id, email, password_hash, full_name, phone, user_type, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, email, password_hash, full_name, phone, user_type, expires_at))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_and_move_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM temp_users WHERE user_id = ? AND expires_at > ?', 
                   (user_id, datetime.now()))
    temp_user = cursor.fetchone()
    
    if temp_user:
        cursor.execute('''
            INSERT INTO users (user_id, email, password_hash, full_name, phone, user_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (temp_user['user_id'], temp_user['email'], temp_user['password_hash'],
              temp_user['full_name'], temp_user['phone'], temp_user['user_type']))
        
        cursor.execute('DELETE FROM temp_users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def create_auth_token(user_id):
    login_time = datetime.now()
    token = generate_auth_token(user_id, login_time)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO auth_tokens (user_id, token, login_time)
        VALUES (?, ?, ?)
    ''', (user_id, token, login_time))
    
    cursor.execute('UPDATE users SET login_status = 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    return token

def verify_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id FROM auth_tokens 
        WHERE token = ? AND is_active = 1
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['user_id'] if result else None

def create_logout_token(user_id):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=15)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logout_tokens (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token

def verify_logout_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id FROM logout_tokens 
        WHERE token = ? AND expires_at > ? AND used = 0
    ''', (token, datetime.now()))
    
    result = cursor.fetchone()
    
    if result:
        cursor.execute('UPDATE logout_tokens SET used = 1 WHERE token = ?', (token,))
        conn.commit()
        user_id = result['user_id']
        conn.close()
        return user_id
    
    conn.close()
    return None

def logout_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE auth_tokens SET is_active = 0 WHERE user_id = ?', (user_id,))
    cursor.execute('UPDATE users SET login_status = 0 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
