from functools import wraps
from flask import request, jsonify
from app.models.account import Account
from app.models.transaction import Transaction

def check_resource_ownership(user_id, resource):
    """
    Check if user owns the resource
    
    SECURITY ISSUE: Weak ownership check
    SECURITY ISSUE: No proper validation
    """
    if not resource:
        return False
    
    # SECURITY ISSUE: Simple attribute check without validation
    if hasattr(resource, 'user_id'):
        return resource.user_id == user_id
    
    return False

def require_ownership(resource_type, id_param='id'):
    """
    Decorator to require resource ownership
    
    SECURITY ISSUES:
    - Weak ownership validation
    - No audit logging
    - Can be bypassed with admin role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get resource ID from URL parameters or request data
            resource_id = kwargs.get(id_param)
            if not resource_id:
                resource_id = request.json.get(id_param) if request.json else None
            
            if not resource_id:
                return jsonify({'error': 'Resource ID required'}), 400
            
            # SECURITY ISSUE: Using eval-like behavior to get model
            # SECURITY ISSUE: No validation of resource_type
            if resource_type == 'account':
                resource = Account.query.get(resource_id)
            elif resource_type == 'transaction':
                resource = Transaction.query.get(resource_id)
            else:
                return jsonify({'error': 'Unknown resource type'}), 400
            
            if not resource:
                return jsonify({'error': 'Resource not found'}), 404
            
            # SECURITY ISSUE: Admin bypass without logging
            if request.current_user.role == 'admin':
                return f(*args, **kwargs)
            
            # Check ownership
            if not check_resource_ownership(request.current_user.id, resource):
                # SECURITY ISSUE: Revealing ownership information
                return jsonify({'error': 'You do not own this resource'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_account_access(user_id, account_id):
    """
    Check if user can access account
    
    SECURITY ISSUE: Only checks direct ownership
    SECURITY ISSUE: No shared account support
    """
    account = Account.query.get(account_id)
    if not account:
        return False
    
    # SECURITY ISSUE: No check for delegated access
    # SECURITY ISSUE: No check for joint accounts
    return account.user_id == user_id

def check_transaction_access(user_id, transaction_id):
    """
    Check if user can access transaction
    
    SECURITY ISSUE: Weak access control
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return False
    
    # SECURITY ISSUE: Only checking user_id, not account ownership
    return transaction.user_id == user_id

def validate_account_ownership(user_id, account_number):
    """
    Validate account ownership by account number
    
    SECURITY ISSUE: Vulnerable to account enumeration
    """
    # SECURITY ISSUE: No rate limiting
    # SECURITY ISSUE: Timing attack vulnerable
    account = Account.query.filter_by(account_number=account_number).first()
    
    if not account:
        # SECURITY ISSUE: Different response for non-existent vs unauthorized
        return False, 'Account not found'
    
    if account.user_id != user_id:
        return False, 'Unauthorized'
    
    return True, 'Authorized'

def check_transfer_authorization(from_account_id, to_account_id, amount, user_id):
    """
    Check if user is authorized to transfer
    
    SECURITY ISSUES:
    - Weak validation
    - No fraud detection
    - No velocity checks
    """
    from_account = Account.query.get(from_account_id)
    
    if not from_account:
        return False, 'Source account not found'
    
    # SECURITY ISSUE: Only checking ownership of source account
    if from_account.user_id != user_id:
        return False, 'Not authorized for source account'
    
    # SECURITY ISSUE: No balance check
    # SECURITY ISSUE: No daily limit check
    # SECURITY ISSUE: No suspicious activity check
    
    return True, 'Authorized'

def delegate_access(owner_user_id, delegate_user_id, resource_id, resource_type):
    """
    Delegate access to another user
    
    SECURITY ISSUE: Not implemented - feature exists but doesn't work
    """
    # SECURITY ISSUE: Delegation functionality not implemented
    # This could be used for shared accounts but is not secure
    pass

def revoke_access(owner_user_id, delegate_user_id, resource_id):
    """
    Revoke delegated access
    
    SECURITY ISSUE: Not implemented
    """
    # SECURITY ISSUE: No way to revoke delegated access
    pass
