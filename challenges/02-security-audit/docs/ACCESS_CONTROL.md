# Access Control Guide - PaySecure

## Overview
This document defines access control policies and implementation guidelines for the PaySecure financial application.

**⚠️ WORKSHOP NOTE: This application contains intentional access control vulnerabilities for training purposes.**

## Access Control Principles

### Core Principles

#### 1. Least Privilege
**Definition:** Users should have minimum access necessary to perform their duties.

**Current Violations:**
```python
# app/permissions/rbac.py:
# All users have read/write access
# No granular permissions
# Admin can access everything without justification
```

#### 2. Separation of Duties
**Definition:** No single individual should have complete control over critical operations.

**Current Violations:**
- Developers have production access
- No approval workflow for sensitive operations
- Single admin can perform all actions

#### 3. Need to Know
**Definition:** Access granted only when required for job function.

**Current Violations:**
- Support can view all customer data
- No time-limited access grants
- No justification required

#### 4. Defense in Depth
**Definition:** Multiple layers of security controls.

**Current Violations:**
- Single authentication factor
- No network segmentation
- Weak session management

## Role-Based Access Control (RBAC)

### Defined Roles

#### User (Basic Customer)
**Permissions:**
- View own account information
- View own transaction history
- Initiate transactions from own accounts
- Update own profile
- Enable/disable MFA

**Current Issues:**
```python
# app/permissions/rbac.py:
ROLE_PERMISSIONS = {
    Role.USER: [Permission.READ, Permission.WRITE]
}
# Too broad - no resource-level control
```

**Should Be:**
```python
USER_PERMISSIONS = {
    'accounts': ['read:own', 'update:own'],
    'transactions': ['read:own', 'create:own'],
    'profile': ['read:own', 'update:own'],
    'payments': ['create:own']
}
```

#### Support Agent
**Permissions:**
- View customer accounts (read-only)
- View transaction history (read-only)
- Reset passwords (with verification)
- View support tickets
- Create notes on accounts

**Restrictions:**
- Cannot initiate transactions
- Cannot modify account balances
- Cannot access payment methods
- Cannot view full SSN or card numbers
- All actions logged

**Current Issues:**
```python
# Support role not implemented
# No read-only enforcement
# Can access all data without restrictions
```

#### Moderator
**Permissions:**
- All Support permissions
- Flag suspicious accounts
- Suspend/unsuspend accounts
- Review flagged transactions
- Access fraud detection tools

**Restrictions:**
- Cannot permanently delete accounts
- Cannot modify transaction history
- Cannot access unmasked payment data

#### Administrator
**Permissions:**
- User management
- Role assignment
- System configuration
- Access to audit logs
- Security settings
- API key management

**Restrictions:**
- Cannot access customer passwords
- Cannot modify audit logs
- Cannot disable security controls without approval
- All actions require MFA
- All actions logged and alerted

**Current Issues:**
```python
# app/permissions/rbac.py:
def check_admin(user):
    return user and user.role == Role.ADMIN
    
# No MFA required for admin actions
# No logging of admin actions
# Can access everything without restrictions
```

### Role Hierarchy

**Proper Hierarchy:**
```
Administrator
    ├── System-level access
    └── Can assign roles
        
Moderator
    ├── All Support permissions
    └── Account management
    
Support Agent
    ├── All User permissions
    └── Read-only customer data
    
User
    └── Own resources only
```

**Current Issue:** No role hierarchy implemented

## Resource-Based Access Control

### Ownership Verification

**Current Vulnerability (IDOR):**
```python
# app/api/accounts.py:
@app.route('/api/accounts/<int:account_id>')
def get_account(account_id):
    account = Account.query.get(account_id)
    return jsonify(account.to_dict())
    
# MISSING: No ownership check!
# Any authenticated user can access any account by changing ID
```

**Required Implementation:**
```python
@app.route('/api/accounts/<int:account_id>')
@require_authentication
def get_account(account_id):
    account = Account.query.get_or_404(account_id)
    
    # Ownership verification
    if account.user_id != current_user.id:
        # Check if admin or support with valid reason
        if not has_permission('accounts:read:any'):
            audit_log('unauthorized_access_attempt', {
                'user_id': current_user.id,
                'resource': 'account',
                'resource_id': account_id
            })
            abort(403, 'Access denied')
        
        # Log privileged access
        audit_log('privileged_access', {
            'user_id': current_user.id,
            'resource': 'account',
            'resource_id': account_id,
            'justification': request.args.get('reason')
        })
    
    return jsonify(account.to_dict(current_user))
```

### Access Control Matrix

| Resource | User | Support | Moderator | Admin |
|----------|------|---------|-----------|-------|
| Own Account | CRUD | R | RU | RUD |
| Other Account | - | R | R | RUD |
| Own Transactions | CR | R | R | R |
| Other Transactions | - | R | R | R |
| Payment Methods | CRUD | - | - | - |
| User Roles | - | - | - | RUD |
| System Config | - | - | - | RUD |
| Audit Logs | R (own) | R (filtered) | R (all) | R (all) |

**Legend:**
- C: Create
- R: Read
- U: Update
- D: Delete
- \-: No access

## Attribute-Based Access Control (ABAC)

### Access Decision Factors

**Current:** Only role checked

**Should Consider:**
1. **User attributes:** Role, department, clearance level
2. **Resource attributes:** Classification, owner, sensitivity
3. **Environment attributes:** Time, location, device
4. **Action attributes:** Read, write, delete, export

### Example Policy
```python
def check_access(user, resource, action, context):
    # Base role check
    if not user.has_permission(f'{resource}:{action}'):
        return False
    
    # Time-based restrictions
    if resource.sensitive and not is_business_hours():
        return False
    
    # Location-based restrictions
    if action == 'export' and not context.ip_in_whitelist():
        return False
    
    # Device-based restrictions
    if resource.highly_sensitive and not context.device_trusted():
        return False
    
    return True
```

**Current Status:** ❌ Not implemented

## Authentication Requirements

### User Authentication

**Current Issues:**
```python
# app/auth/password.py:
- MD5 password hashing (weak)
- No account lockout after failed attempts
- No CAPTCHA after multiple failures
- JWT valid for 30 days
- No device fingerprinting
```

**Required:**
- bcrypt/Argon2 password hashing (work factor 12+)
- Account lockout: 5 failed attempts, 15-minute lockout
- CAPTCHA after 3 failed attempts
- JWT expiration: 1 hour for regular, 15 minutes for sensitive operations
- Device fingerprinting and tracking

### Multi-Factor Authentication (MFA)

**Current Issues:**
```python
# app/auth/mfa.py:
- MFA secret exposed in API responses
- No rate limiting on MFA verification
- Wide time window for TOTP codes
- MFA not required for admin actions
```

**Required Implementation:**
- MFA secrets encrypted and never exposed
- Rate limiting: 5 attempts per 5 minutes
- Standard TOTP time window (30 seconds)
- MFA required for:
  - Admin actions
  - Large transactions (> $1,000)
  - Sensitive data access
  - Role changes
  - Security settings changes

### Session Management

**Current Issues:**
```python
# app/auth/sessions.py:
sessions = {}  # In-memory only (lost on restart)

def create_session(user_id, username, ip_address):
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        'user_id': user_id,
        'username': username,
        'ip_address': ip_address,
        'created_at': datetime.now()
    }
    # No expiration!
    # No IP validation!
    return session_id
```

**Required:**
```python
def create_session(user_id, username, ip_address, user_agent):
    session_id = secrets.token_urlsafe(32)
    
    session = Session(
        session_id=session_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        last_activity=datetime.now()
    )
    db.session.add(session)
    db.session.commit()
    
    return session_id

def validate_session(session_id, ip_address, user_agent):
    session = Session.query.filter_by(session_id=session_id).first()
    
    if not session:
        return None
    
    # Check expiration
    if session.expires_at < datetime.now():
        db.session.delete(session)
        db.session.commit()
        return None
    
    # Check IP address
    if session.ip_address != ip_address:
        audit_log('session_ip_mismatch', {
            'session_id': session_id,
            'expected_ip': session.ip_address,
            'actual_ip': ip_address
        })
        return None
    
    # Check user agent
    if session.user_agent != user_agent:
        audit_log('session_ua_mismatch', {
            'session_id': session_id
        })
        return None
    
    # Update last activity
    session.last_activity = datetime.now()
    db.session.commit()
    
    return session
```

## Authorization Checks

### Decorator-Based Authorization

**Current Issues:**
```python
# app/api/decorators.py:
def require_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token'}), 401
        
        # Weak JWT validation
        # No token blacklist check
        # No permission verification
        
        return f(*args, **kwargs)
    return decorated
```

**Required Implementation:**
```python
def require_permission(resource, action):
    """
    Decorator to require specific permission
    
    @require_permission('accounts', 'read')
    def get_account(account_id):
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 1. Verify authentication
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # 2. Check if token is blacklisted
            if is_token_blacklisted(current_user.token):
                return jsonify({'error': 'Token revoked'}), 401
            
            # 3. Verify session validity
            if not validate_session(current_user.session_id):
                return jsonify({'error': 'Invalid session'}), 401
            
            # 4. Check permission
            if not has_permission(current_user, resource, action):
                audit_log('authorization_failure', {
                    'user_id': current_user.id,
                    'resource': resource,
                    'action': action,
                    'endpoint': request.endpoint
                })
                return jsonify({'error': 'Permission denied'}), 403
            
            # 5. Check additional context (time, location, etc.)
            if not check_context(current_user, resource, action):
                return jsonify({'error': 'Access not allowed in current context'}), 403
            
            # 6. Log access
            audit_log('resource_access', {
                'user_id': current_user.id,
                'resource': resource,
                'action': action,
                'resource_id': kwargs.get('id')
            })
            
            return f(*args, **kwargs)
        return decorated
    return decorator
```

### Resource-Level Authorization

**Example: Transaction Access**
```python
@app.route('/api/transactions/<int:transaction_id>')
@require_permission('transactions', 'read')
def get_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Additional resource-level check
    if not can_access_transaction(current_user, transaction):
        abort(403, 'You do not have access to this transaction')
    
    return jsonify(transaction.to_dict(current_user))

def can_access_transaction(user, transaction):
    # User can access own transactions
    if transaction.user_id == user.id:
        return True
    
    # User can access transactions from owned accounts
    if transaction.account.user_id == user.id:
        return True
    
    # Support/Admin with proper justification
    if user.role in ['support', 'admin']:
        reason = request.args.get('reason')
        if reason:
            audit_log('privileged_transaction_access', {
                'user_id': user.id,
                'transaction_id': transaction.id,
                'reason': reason
            })
            return True
    
    return False
```

## Privilege Escalation Prevention

### Current Vulnerability
```python
# app/permissions/rbac.py:
def elevate_privileges(user, target_role):
    # CRITICAL: No authorization check!
    user.role = target_role
    return True

# Anyone can call this to become admin!
```

### Required Implementation
```python
def elevate_privileges(admin_user, target_user, target_role, justification):
    # 1. Verify admin is authenticated
    if not admin_user or not admin_user.is_authenticated:
        raise Unauthorized('Authentication required')
    
    # 2. Verify admin has permission
    if not has_permission(admin_user, 'users', 'update_role'):
        raise Forbidden('Permission denied')
    
    # 3. Require MFA for role changes
    if not verify_mfa_for_action(admin_user):
        raise Forbidden('MFA verification required')
    
    # 4. Validate target role
    if target_role not in VALID_ROLES:
        raise ValueError('Invalid role')
    
    # 5. Prevent self-elevation to admin
    if admin_user.id == target_user.id and target_role == 'admin':
        raise Forbidden('Cannot self-elevate to admin')
    
    # 6. Require justification
    if not justification or len(justification) < 10:
        raise ValueError('Justification required')
    
    # 7. Log role change
    old_role = target_user.role
    audit_log('role_change', {
        'admin_id': admin_user.id,
        'target_user_id': target_user.id,
        'old_role': old_role,
        'new_role': target_role,
        'justification': justification
    })
    
    # 8. Alert security team for admin role changes
    if target_role == 'admin':
        send_security_alert('admin_role_assigned', {
            'admin': admin_user.username,
            'new_admin': target_user.username
        })
    
    # 9. Perform role change
    target_user.role = target_role
    db.session.commit()
    
    # 10. Invalidate user's existing sessions
    invalidate_user_sessions(target_user.id)
    
    return True
```

## Access Control Lists (ACLs)

### Resource-Specific ACLs
**Use Case:** Shared accounts, delegated access

```python
class AccountACL(db.Model):
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    permission = Column(String(50))  # 'read', 'write', 'admin'
    granted_by = Column(Integer, ForeignKey('user.id'))
    granted_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    
def check_acl_permission(user_id, account_id, permission):
    acl = AccountACL.query.filter_by(
        account_id=account_id,
        user_id=user_id
    ).first()
    
    if not acl:
        return False
    
    # Check expiration
    if acl.expires_at and acl.expires_at < datetime.now():
        return False
    
    # Check permission level
    if acl.permission == 'admin':
        return True
    if acl.permission == 'write' and permission in ['read', 'write']:
        return True
    if acl.permission == 'read' and permission == 'read':
        return True
    
    return False
```

**Current Status:** ❌ Not implemented

## Audit Logging

### What to Log
1. **Authentication events:** Login, logout, failures
2. **Authorization failures:** Permission denied
3. **Resource access:** Viewing sensitive data
4. **Data modifications:** Create, update, delete
5. **Administrative actions:** Role changes, config updates
6. **Privileged access:** Admin viewing customer data

### Current Issues
```python
# app/services/audit_logger.py:
# Minimal logging
# No structured format
# Missing critical events
# No real-time alerting
```

### Required Format
```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "resource_access",
    "user_id": 123,
    "username": "jsmith",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "resource_type": "account",
    "resource_id": 456,
    "action": "read",
    "result": "success",
    "justification": "Customer support ticket #789"
}
```

## Access Reviews

### Regular Reviews Required
- **Weekly:** Failed access attempts
- **Monthly:** User permissions audit
- **Quarterly:** Role assignments review
- **Annually:** Comprehensive access audit

### Access Review Process
1. List all user accounts and permissions
2. Verify each access is still required
3. Remove unnecessary access
4. Update roles as needed
5. Document changes

---

**Last Updated:** 2024
**Version:** 1.0 (Training Exercise)
**Review Frequency:** Quarterly
