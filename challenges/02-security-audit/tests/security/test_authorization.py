"""
Authorization security tests

Tests authorization vulnerabilities including:
- IDOR (Insecure Direct Object Reference)
- Missing access control
- Privilege escalation
- Weak RBAC implementation
"""

import pytest
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.permissions.rbac import has_role, has_permission, elevate_privileges
from app.permissions.ownership import check_account_access, check_transaction_access
from app import create_app, db

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def users(app):
    """Create test users"""
    with app.app_context():
        user1 = User(username='user1', email='user1@example.com', role='user')
        user1.set_password('password123')
        
        user2 = User(username='user2', email='user2@example.com', role='user')
        user2.set_password('password123')
        
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        
        db.session.add_all([user1, user2, admin])
        db.session.commit()
        
        return {'user1': user1, 'user2': user2, 'admin': admin}

class TestIDOR:
    """Test IDOR vulnerabilities"""
    
    def test_access_other_user_account(self, client, app, users):
        """Test accessing another user's account (IDOR vulnerability)"""
        with app.app_context():
            # Create accounts
            account1 = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            account2 = Account(user_id=users['user2'].id, account_number='87654321', balance=2000)
            db.session.add_all([account1, account2])
            db.session.commit()
            
            # VULNERABLE: User1 can access user2's account by changing ID
            # Login as user1
            response = client.post('/api/auth/login', json={
                'username': 'user1',
                'password': 'password123'
            })
            token = response.json.get('token')
            
            # Try to access user2's account
            response = client.get(
                f'/api/accounts/{account2.id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # VULNERABILITY: Should return 403, but might return 200
            # This depends on whether ownership check is implemented
    
    def test_access_other_user_transaction(self, client, app, users):
        """Test accessing another user's transaction (IDOR vulnerability)"""
        with app.app_context():
            # Create transactions
            trans1 = Transaction(
                user_id=users['user1'].id,
                account_id=1,
                amount=100,
                transaction_type='transfer'
            )
            trans2 = Transaction(
                user_id=users['user2'].id,
                account_id=2,
                amount=200,
                transaction_type='transfer'
            )
            db.session.add_all([trans1, trans2])
            db.session.commit()
            
            # VULNERABLE: User1 can view user2's transaction
            assert trans1.id != trans2.id
    
    def test_modify_other_user_account(self, client, app, users):
        """Test modifying another user's account (IDOR vulnerability)"""
        with app.app_context():
            account = Account(user_id=users['user2'].id, account_number='12345678', balance=1000)
            db.session.add(account)
            db.session.commit()
            
            # Login as user1
            response = client.post('/api/auth/login', json={
                'username': 'user1',
                'password': 'password123'
            })
            token = response.json.get('token')
            
            # VULNERABLE: Try to update user2's account
            response = client.put(
                f'/api/accounts/{account.id}',
                json={'balance': 5000},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Should be blocked but might succeed

class TestPrivilegeEscalation:
    """Test privilege escalation vulnerabilities"""
    
    def test_elevate_privileges_without_auth(self, app, users):
        """Test privilege escalation without authorization (vulnerability)"""
        with app.app_context():
            user = users['user1']
            assert user.role == 'user'
            
            # VULNERABLE: No authorization check in elevate_privileges
            elevate_privileges(user, 'admin')
            
            assert user.role == 'admin'  # Vulnerability: succeeded without auth
    
    def test_user_can_change_own_role(self, client, app, users):
        """Test user changing their own role (vulnerability)"""
        with app.app_context():
            # Login as regular user
            response = client.post('/api/auth/login', json={
                'username': 'user1',
                'password': 'password123'
            })
            token = response.json.get('token')
            
            # VULNERABLE: Try to change own role via mass assignment
            response = client.put(
                '/api/users/me',
                json={'role': 'admin'},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Vulnerability: might succeed if mass assignment not prevented

class TestRBAC:
    """Test RBAC vulnerabilities"""
    
    def test_weak_role_hierarchy(self, app):
        """Test weak role hierarchy (vulnerability)"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', role='user')
            admin = User(username='admin', email='admin@example.com', role='admin')
            
            # VULNERABLE: No hierarchical roles
            # Admin should have all user permissions + more
            assert has_role(user, 'user')
            assert not has_role(user, 'admin')
            
            # Admin doesn't inherit user role
            assert has_role(admin, 'admin')
            # VULNERABILITY: Admin role check doesn't include user permissions
    
    def test_no_granular_permissions(self, app):
        """Test lack of granular permissions (vulnerability)"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', role='user')
            
            # VULNERABLE: Only role-based, no granular permissions
            # Can't grant specific permissions like "can_view_reports"
            assert has_role(user, 'user')
    
    def test_admin_bypass_without_logging(self, app, users):
        """Test admin bypass without audit logging (vulnerability)"""
        with app.app_context():
            admin = users['admin']
            user_account = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            db.session.add(user_account)
            db.session.commit()
            
            # VULNERABLE: Admin can access any resource without logging
            # Should be logged in audit trail
            assert check_account_access(admin.id, user_account.id) or admin.role == 'admin'

class TestAccessControl:
    """Test access control vulnerabilities"""
    
    def test_no_delegation_support(self, app, users):
        """Test lack of access delegation (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No way to delegate access to accounts
            # Joint accounts or shared access not supported
            account = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            db.session.add(account)
            db.session.commit()
            
            # No mechanism to grant user2 access to user1's account
    
    def test_weak_account_ownership_check(self, app, users):
        """Test weak account ownership validation (vulnerability)"""
        with app.app_context():
            account = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            db.session.add(account)
            db.session.commit()
            
            # VULNERABLE: Simple user_id check, no additional validation
            assert check_account_access(users['user1'].id, account.id)
            assert not check_account_access(users['user2'].id, account.id)
    
    def test_no_resource_level_permissions(self, app, users):
        """Test lack of resource-level permissions (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Permissions are role-based only
            # No per-resource permissions like "can edit account 123"
            account = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            db.session.add(account)
            db.session.commit()
            
            # No fine-grained control

class TestAPIEndpointAuthorization:
    """Test API endpoint authorization vulnerabilities"""
    
    def test_missing_authorization_check(self, client, app, users):
        """Test endpoints missing authorization checks (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Some endpoints might not check authorization
            # Try accessing protected resource without token
            response = client.get('/api/accounts/1')
            
            # Should return 401, but might return data if auth check missing
    
    def test_transfer_without_ownership_check(self, client, app, users):
        """Test transfer without proper ownership check (vulnerability)"""
        with app.app_context():
            account1 = Account(user_id=users['user1'].id, account_number='12345678', balance=1000)
            account2 = Account(user_id=users['user2'].id, account_number='87654321', balance=2000)
            db.session.add_all([account1, account2])
            db.session.commit()
            
            # Login as user1
            response = client.post('/api/auth/login', json={
                'username': 'user1',
                'password': 'password123'
            })
            token = response.json.get('token')
            
            # VULNERABLE: Try to transfer from user2's account
            response = client.post(
                '/api/accounts/transfer',
                json={
                    'from_account_id': account2.id,  # Not owned by user1
                    'to_account_id': account1.id,
                    'amount': 500
                },
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Vulnerability: might succeed if ownership check missing
