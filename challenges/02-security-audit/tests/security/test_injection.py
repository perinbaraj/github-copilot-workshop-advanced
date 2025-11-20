"""
SQL Injection security tests

Tests SQL injection vulnerabilities including:
- Classic SQL injection
- Blind SQL injection
- Time-based SQL injection
- Union-based injection
"""

import pytest
from app.models.user import User
from app.models.transaction import Transaction
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
def authenticated_client(client, app):
    """Create authenticated test client"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        token = response.json.get('token')
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        return client

class TestSQLInjection:
    """Test SQL injection vulnerabilities"""
    
    def test_sql_injection_in_search(self, authenticated_client, app):
        """Test SQL injection in transaction search (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Search endpoint uses string concatenation
            # Payload: ' OR '1'='1
            response = authenticated_client.get(
                "/api/transactions/search?query=' OR '1'='1"
            )
            
            # Vulnerability: might return all transactions
            # Should use parameterized queries
    
    def test_union_based_injection(self, authenticated_client, app):
        """Test UNION-based SQL injection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: UNION injection to extract data
            # Payload: ' UNION SELECT id, username, password_hash FROM users --
            payload = "' UNION SELECT id, username, password_hash FROM users --"
            
            response = authenticated_client.get(
                f"/api/transactions/search?query={payload}"
            )
            
            # Vulnerability: might expose user data
    
    def test_time_based_blind_injection(self, authenticated_client, app):
        """Test time-based blind SQL injection (vulnerability)"""
        with app.app_context():
            import time
            
            # VULNERABLE: Time-based injection
            # Payload: ' AND SLEEP(5) --
            start_time = time.time()
            
            response = authenticated_client.get(
                "/api/transactions/search?query=' AND SLEEP(5) --"
            )
            
            elapsed_time = time.time() - start_time
            
            # Vulnerability: query might be delayed if injection works
    
    def test_boolean_based_blind_injection(self, authenticated_client, app):
        """Test boolean-based blind SQL injection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Boolean-based injection
            # Payload variations to determine true/false
            response1 = authenticated_client.get(
                "/api/transactions/search?query=' AND '1'='1"
            )
            
            response2 = authenticated_client.get(
                "/api/transactions/search?query=' AND '1'='2"
            )
            
            # Vulnerability: different responses indicate injection
    
    def test_injection_in_order_by(self, authenticated_client, app):
        """Test SQL injection in ORDER BY clause (vulnerability)"""
        with app.app_context():
            # VULNERABLE: ORDER BY injection
            # Payload: amount; DROP TABLE transactions; --
            response = authenticated_client.get(
                "/api/transactions?sort=amount; DROP TABLE transactions; --"
            )
            
            # Vulnerability: might execute malicious SQL
    
    def test_injection_in_filter(self, authenticated_client, app):
        """Test SQL injection in filter parameters (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Filter injection
            # Payload: 1' OR '1'='1' --
            response = authenticated_client.get(
                "/api/transactions?account_id=1' OR '1'='1' --"
            )
            
            # Vulnerability: might bypass filter

class TestParameterizedQueries:
    """Test if parameterized queries are used"""
    
    def test_raw_sql_usage(self, app):
        """Test if raw SQL with string concatenation is used (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Code uses f-strings or + for SQL
            # Check transaction search implementation
            
            # This test documents the vulnerability
            # Real code in transactions.py uses:
            # query = f"SELECT * FROM transactions WHERE description LIKE '%{search_term}%'"
            pass
    
    def test_orm_not_used(self, app):
        """Test that ORM is bypassed with raw SQL (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Using db.session.execute with raw SQL
            # instead of SQLAlchemy ORM
            pass

class TestSecondOrderInjection:
    """Test second-order SQL injection vulnerabilities"""
    
    def test_stored_xss_via_sql_injection(self, authenticated_client, app):
        """Test second-order injection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Inject malicious SQL via one endpoint
            # that gets executed later in another query
            
            # Step 1: Store malicious data
            response = authenticated_client.post('/api/transactions', json={
                'amount': 100,
                'description': "'; DROP TABLE users; --",
                'account_id': 1
            })
            
            # Step 2: Malicious data used in another query
            response = authenticated_client.get('/api/transactions/search?query=test')
            
            # Vulnerability: stored data might be used in unsafe query

class TestInjectionInDifferentContexts:
    """Test SQL injection in various contexts"""
    
    def test_injection_in_like_clause(self, authenticated_client, app):
        """Test SQL injection in LIKE clause (vulnerability)"""
        with app.app_context():
            # VULNERABLE: LIKE with unescaped wildcards
            response = authenticated_client.get(
                "/api/transactions/search?query=%' OR '1'='1' OR '%'='"
            )
    
    def test_injection_in_in_clause(self, authenticated_client, app):
        """Test SQL injection in IN clause (vulnerability)"""
        with app.app_context():
            # VULNERABLE: IN clause with string concatenation
            response = authenticated_client.get(
                "/api/transactions?ids=1,2,3) OR 1=1 --"
            )
    
    def test_injection_in_limit_clause(self, authenticated_client, app):
        """Test SQL injection in LIMIT clause (vulnerability)"""
        with app.app_context():
            # VULNERABLE: LIMIT injection
            response = authenticated_client.get(
                "/api/transactions?limit=10; DELETE FROM transactions; --"
            )

class TestNoSQLInjection:
    """Test NoSQL injection if MongoDB is used"""
    
    def test_nosql_operator_injection(self, authenticated_client, app):
        """Test NoSQL operator injection (vulnerability)"""
        with app.app_context():
            # If using MongoDB
            # VULNERABLE: Operator injection
            response = authenticated_client.post('/api/auth/login', json={
                'username': {'$ne': None},
                'password': {'$ne': None}
            })
            
            # Vulnerability: might bypass authentication
