from functools import wraps
from flask import request, jsonify
import jwt
from app.models.user import User

# SECURITY ISSUE: Weak JWT validation
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # SECURITY ISSUE: Token format not validated properly
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            # SECURITY ISSUE: Weak secret key
            data = jwt.decode(token, 'jwt-secret', algorithms=['HS256'])
            
            # SECURITY ISSUE: No token expiration check
            # SECURITY ISSUE: No token blacklist
            
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
            
            request.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            # SECURITY ISSUE: Exposing internal errors
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# SECURITY ISSUE: No role-based access control
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # SECURITY ISSUE: No proper authentication check
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # SECURITY ISSUE: Role check is weak
        if request.current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

# SECURITY ISSUE: No resource ownership validation
def owner_required(resource_user_id_field='user_id'):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # SECURITY ISSUE: Weak ownership check
            resource_user_id = kwargs.get(resource_user_id_field)
            
            if request.current_user.id != resource_user_id and request.current_user.role != 'admin':
                return jsonify({'error': 'Access denied'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

# SECURITY ISSUE: No input validation decorator
def validate_input(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            
            # SECURITY ISSUE: Minimal validation
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # SECURITY ISSUE: No type validation
            # SECURITY ISSUE: No sanitization
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator
