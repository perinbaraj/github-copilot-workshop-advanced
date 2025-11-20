from functools import wraps
from flask import request, jsonify

# SECURITY ISSUE: Simple role-based system with no granular permissions

class Role:
    """
    Role definitions
    
    SECURITY ISSUE: No hierarchical roles
    SECURITY ISSUE: No permission inheritance
    """
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    
    # SECURITY ISSUE: All roles hardcoded

class Permission:
    """
    Permission definitions
    
    SECURITY ISSUE: Not properly implemented
    """
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    ADMIN = 'admin'

# SECURITY ISSUE: Role permissions mapping is too permissive
ROLE_PERMISSIONS = {
    Role.USER: [Permission.READ, Permission.WRITE],
    Role.MODERATOR: [Permission.READ, Permission.WRITE, Permission.DELETE],
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN]
}

def has_role(user, required_role):
    """
    Check if user has required role
    
    SECURITY ISSUE: Simple string comparison, no hierarchy
    """
    if not user:
        return False
    
    # SECURITY ISSUE: Direct role comparison without hierarchy
    return user.role == required_role

def has_permission(user, required_permission):
    """
    Check if user has required permission
    
    SECURITY ISSUE: Not properly validated
    """
    if not user:
        return False
    
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return required_permission in user_permissions

def require_role(role):
    """
    Decorator to require specific role
    
    SECURITY ISSUE: Weak role check
    SECURITY ISSUE: No audit logging
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # SECURITY ISSUE: No session validation
            # SECURITY ISSUE: No IP check
            
            if not has_role(request.current_user, role):
                # SECURITY ISSUE: Revealing role information in error
                return jsonify({'error': f'Role {role} required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    """
    Decorator to require specific permission
    
    SECURITY ISSUE: Not properly implemented
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if not has_permission(request.current_user, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_any_role(*roles):
    """
    Decorator to require any of the specified roles
    
    SECURITY ISSUE: Logical flaw in implementation
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # SECURITY ISSUE: Using 'or' in loop - can be bypassed
            user_has_role = False
            for role in roles:
                if has_role(request.current_user, role):
                    user_has_role = True
                    break
            
            if not user_has_role:
                return jsonify({'error': 'Unauthorized'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_admin(user):
    """
    Check if user is admin
    
    SECURITY ISSUE: Weak admin check
    """
    # SECURITY ISSUE: Only checking role, not validating session
    return user and user.role == Role.ADMIN

def elevate_privileges(user, target_role):
    """
    Elevate user privileges
    
    SECURITY ISSUE: No authorization check for privilege elevation
    SECURITY ISSUE: No audit logging
    SECURITY ISSUE: No temporary privilege elevation
    """
    # SECURITY ISSUE: Anyone can call this function
    user.role = target_role
    return True

def check_resource_access(user, resource_type, resource_id, action):
    """
    Check if user can access specific resource
    
    SECURITY ISSUE: Not properly implemented
    SECURITY ISSUE: No fine-grained access control
    """
    # SECURITY ISSUE: Placeholder implementation
    return has_role(user, Role.ADMIN)
