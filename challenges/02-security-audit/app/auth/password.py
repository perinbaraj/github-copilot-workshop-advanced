import hashlib
import re
from app.auth import auth_bp
from app.models.user import User
from app import db
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta

# SECURITY ISSUE: Weak password hashing using MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, password_hash):
    # SECURITY ISSUE: Timing attack vulnerable
    return hash_password(password) == password_hash

# SECURITY ISSUE: Weak password validation
def validate_password(password):
    if len(password) < 4:  # SECURITY ISSUE: Too short minimum length
        return False, "Password must be at least 4 characters"
    
    # SECURITY ISSUE: No complexity requirements
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input validation
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # SECURITY ISSUE: No CAPTCHA for signup
        
        # Weak password validation
        valid, message = validate_password(password)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # SECURITY ISSUE: No email validation
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)  # Uses weak MD5 hashing
        
        db.session.add(user)
        db.session.commit()
        
        # SECURITY ISSUE: Returning sensitive user data
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()  # Exposes sensitive data
        }), 201
        
    except Exception as e:
        # SECURITY ISSUE: Exposing internal errors
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input sanitization
        username = data.get('username')
        password = data.get('password')
        
        # SECURITY ISSUE: No rate limiting on login attempts
        
        # SECURITY ISSUE: Username enumeration vulnerability
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'Invalid username'}), 401  # Reveals username doesn't exist
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            return jsonify({'error': 'Account is locked'}), 403
        
        if not user.check_password(password):
            user.failed_login_attempts += 1
            
            # SECURITY ISSUE: Too many attempts before lockout
            if user.failed_login_attempts >= 10:
                user.locked_until = datetime.utcnow() + timedelta(minutes=5)
            
            db.session.commit()
            return jsonify({'error': 'Invalid password'}), 401
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        # SECURITY ISSUE: Weak JWT configuration
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(days=30)  # SECURITY ISSUE: Long expiration
        }, 'jwt-secret', algorithm='HS256')  # SECURITY ISSUE: Weak secret
        
        # SECURITY ISSUE: No session management
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()  # SECURITY ISSUE: Exposing sensitive data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No authentication check
        user_id = data.get('user_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # SECURITY ISSUE: No verification of old password
        
        # Validate new password
        valid, message = validate_password(new_password)
        if not valid:
            return jsonify({'error': message}), 400
        
        # SECURITY ISSUE: No check if new password is same as old password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
