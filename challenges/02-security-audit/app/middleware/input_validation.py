from flask import request, jsonify
from functools import wraps
import re
import html

def validate_input(schema):
    """
    Validate request input against schema
    
    SECURITY ISSUES:
    - Minimal validation
    - No sanitization
    - Schema not enforced
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            # SECURITY ISSUE: Not actually validating against schema
            # Just checking if required fields exist
            for field in schema.get('required', []):
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # SECURITY ISSUE: No type validation
            # SECURITY ISSUE: No sanitization
            # SECURITY ISSUE: No length validation
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_string(value):
    """
    Sanitize string input
    
    SECURITY ISSUE: Incomplete sanitization
    """
    if not isinstance(value, str):
        return value
    
    # SECURITY ISSUE: Only escaping HTML, not preventing SQL injection
    # SECURITY ISSUE: Not removing dangerous characters
    return html.escape(value)

def validate_email(email):
    """
    Validate email address
    
    SECURITY ISSUE: Weak email validation regex
    """
    # SECURITY ISSUE: Regex too permissive, allows invalid emails
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate phone number
    
    SECURITY ISSUE: No validation
    """
    # SECURITY ISSUE: Phone validation not implemented
    return True

def validate_account_number(account_number):
    """
    Validate account number
    
    SECURITY ISSUE: Weak validation
    """
    # SECURITY ISSUE: Only checking length, no checksum validation
    if not isinstance(account_number, str):
        return False
    
    # SECURITY ISSUE: Allowing any numeric string
    return len(account_number) >= 8 and account_number.isdigit()

def validate_amount(amount):
    """
    Validate monetary amount
    
    SECURITY ISSUE: Insufficient validation
    """
    try:
        amount = float(amount)
        # SECURITY ISSUE: Allowing negative amounts
        # SECURITY ISSUE: No maximum amount check
        # SECURITY ISSUE: No precision validation
        return amount > 0
    except (ValueError, TypeError):
        return False

def sanitize_sql_input(value):
    """
    Sanitize SQL input
    
    SECURITY ISSUE: Blacklist approach instead of parameterized queries
    """
    if not isinstance(value, str):
        return value
    
    # SECURITY ISSUE: Blacklist is incomplete and bypassable
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'INSERT', 'DELETE', 'UPDATE']
    
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    # SECURITY ISSUE: This approach is fundamentally flawed
    return value

def validate_json_input(data, allowed_fields):
    """
    Validate JSON input
    
    SECURITY ISSUE: Not preventing extra fields
    """
    if not isinstance(data, dict):
        return False, 'Invalid data format'
    
    # SECURITY ISSUE: Only checking if fields exist, not preventing extra fields
    # SECURITY ISSUE: Mass assignment vulnerability
    for field in allowed_fields:
        if field not in data:
            return False, f'Missing field: {field}'
    
    return True, 'Valid'

def sanitize_filename(filename):
    """
    Sanitize filename
    
    SECURITY ISSUE: Incomplete sanitization
    """
    if not filename:
        return 'unnamed'
    
    # SECURITY ISSUE: Not preventing directory traversal
    # SECURITY ISSUE: Not checking file extension
    # SECURITY ISSUE: Allowing dangerous characters
    
    # Only removing some dangerous characters
    filename = filename.replace('/', '_').replace('\\', '_')
    
    return filename

def validate_password_strength(password):
    """
    Validate password strength
    
    SECURITY ISSUE: Very weak password requirements
    """
    if not password:
        return False, 'Password is required'
    
    # SECURITY ISSUE: Minimum length too short
    if len(password) < 4:
        return False, 'Password must be at least 4 characters'
    
    # SECURITY ISSUE: No complexity requirements
    # SECURITY ISSUE: Not checking for common passwords
    # SECURITY ISSUE: Not checking password breaches
    
    return True, 'Password accepted'

def prevent_xss(value):
    """
    Prevent XSS attacks
    
    SECURITY ISSUE: Incomplete XSS prevention
    """
    if not isinstance(value, str):
        return value
    
    # SECURITY ISSUE: Only escaping basic HTML
    # SECURITY ISSUE: Not handling all XSS vectors
    # SECURITY ISSUE: Not context-aware
    
    return html.escape(value, quote=True)

class InputValidator:
    """
    Input validation class
    
    SECURITY ISSUE: Not actually used consistently
    """
    
    @staticmethod
    def validate_user_input(data):
        """
        Validate user input
        
        SECURITY ISSUE: Placeholder implementation
        """
        # SECURITY ISSUE: No actual validation
        return True
    
    @staticmethod
    def validate_transaction_input(data):
        """
        Validate transaction input
        
        SECURITY ISSUE: Minimal validation
        """
        required_fields = ['amount', 'account_id']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # SECURITY ISSUE: Not validating field values
        return True
