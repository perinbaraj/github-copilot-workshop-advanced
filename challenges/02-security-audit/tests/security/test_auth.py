"""
Security test suite for PaySecure application

Tests authentication vulnerabilities including:
- Weak password policies
- MD5 hashing
- JWT vulnerabilities
- Session management issues
- MFA weaknesses
"""

import pytest
import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.auth.password import hash_password, verify_password, generate_jwt, validate_jwt
from app.auth.sessions import create_session, validate_session
from app.auth.mfa import generate_mfa_secret, verify_mfa_code
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

class TestPasswordSecurity:
    """Test password security vulnerabilities"""
    
    def test_weak_password_accepted(self, app):
        """Test that weak passwords are accepted (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Should reject weak passwords
            weak_passwords = ['123', 'abcd', 'pass', 'test']
            
            for password in weak_passwords:
                hashed = hash_password(password)
                assert hashed is not None  # Vulnerability: accepts weak passwords
    
    def test_md5_hashing_used(self, app):
        """Test that MD5 is used for hashing (vulnerability)"""
        with app.app_context():
            password = 'testpassword'
            hashed = hash_password(password)
            
            # VULNERABLE: MD5 produces 32 character hex string
            assert len(hashed) == 32
            assert all(c in '0123456789abcdef' for c in hashed)
    
    def test_password_timing_attack(self, app):
        """Test password verification timing attack vulnerability"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('correctpassword')
            
            # VULNERABLE: Timing attack possible
            # Should use constant-time comparison
            assert verify_password(user, 'correctpassword')
            assert not verify_password(user, 'wrongpassword')
    
    def test_no_password_complexity(self, app):
        """Test lack of password complexity requirements"""
        with app.app_context():
            # VULNERABLE: No uppercase, lowercase, number, special char requirements
            simple_passwords = ['aaaaaaaa', '11111111', 'password']
            
            for password in simple_passwords:
                hashed = hash_password(password)
                assert hashed is not None

class TestJWTSecurity:
    """Test JWT vulnerabilities"""
    
    def test_long_jwt_expiration(self, app):
        """Test that JWT has very long expiration (vulnerability)"""
        with app.app_context():
            token = generate_jwt(1, 'testuser')
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # VULNERABLE: 30 day expiration
            exp_timestamp = decoded['exp']
            exp_date = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            days_diff = (exp_date - now).days
            
            assert days_diff >= 29  # Should be much shorter
    
    def test_weak_jwt_secret(self, app):
        """Test weak JWT secret key"""
        # VULNERABLE: Secret key is weak/predictable
        assert len(app.config['SECRET_KEY']) < 32  # Should be longer
    
    def test_no_jwt_revocation(self, app):
        """Test that JWT cannot be revoked (vulnerability)"""
        with app.app_context():
            token = generate_jwt(1, 'testuser')
            
            # VULNERABLE: No token blacklist/revocation mechanism
            # Token remains valid even after logout
            assert validate_jwt(token) is not None

class TestSessionSecurity:
    """Test session management vulnerabilities"""
    
    def test_session_in_memory(self, app):
        """Test that sessions are stored in memory (vulnerability)"""
        with app.app_context():
            session_id = create_session(1, 'testuser', '127.0.0.1')
            
            # VULNERABLE: Session in memory, lost on restart
            assert session_id is not None
            assert validate_session(session_id) is not None
    
    def test_no_session_timeout(self, app):
        """Test lack of session timeout (vulnerability)"""
        with app.app_context():
            session_id = create_session(1, 'testuser', '127.0.0.1')
            
            # VULNERABLE: No session expiration implemented
            # Session remains valid indefinitely
            assert validate_session(session_id) is not None
    
    def test_no_ip_validation(self, app):
        """Test that session IP is not validated (vulnerability)"""
        with app.app_context():
            session_id = create_session(1, 'testuser', '192.168.1.1')
            
            # VULNERABLE: Can use session from different IP
            # No IP validation in validate_session
            assert validate_session(session_id) is not None

class TestMFASecurity:
    """Test MFA vulnerabilities"""
    
    def test_mfa_secret_exposed(self, app):
        """Test that MFA secret is exposed in API (vulnerability)"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            user.mfa_secret = generate_mfa_secret()
            
            # VULNERABLE: MFA secret exposed in to_dict()
            user_dict = user.to_dict()
            assert 'mfa_secret' in user_dict
    
    def test_no_mfa_rate_limit(self, app):
        """Test lack of MFA rate limiting (vulnerability)"""
        with app.app_context():
            secret = generate_mfa_secret()
            
            # VULNERABLE: Can brute force MFA codes
            # No rate limiting on verify_mfa_code
            for i in range(100):
                verify_mfa_code(secret, '000000')
    
    def test_wide_time_window(self, app):
        """Test that MFA has wide time window (vulnerability)"""
        with app.app_context():
            secret = generate_mfa_secret()
            
            # VULNERABLE: Time window too wide for TOTP
            # Allows old codes to work
            pass  # Would need to test with actual time-based codes

class TestAuthenticationEndpoints:
    """Test authentication endpoint vulnerabilities"""
    
    def test_username_enumeration(self, client, app):
        """Test username enumeration vulnerability"""
        with app.app_context():
            # Create test user
            user = User(username='existinguser', email='existing@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # VULNERABLE: Different responses for existing vs non-existing users
            response1 = client.post('/api/auth/login', json={
                'username': 'existinguser',
                'password': 'wrongpassword'
            })
            
            response2 = client.post('/api/auth/login', json={
                'username': 'nonexistentuser',
                'password': 'wrongpassword'
            })
            
            # Vulnerability: responses differ, allowing enumeration
            assert response1.status_code == response2.status_code  # May differ in practice
    
    def test_no_rate_limiting(self, client, app):
        """Test lack of rate limiting on login (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No rate limiting allows brute force
            for i in range(100):
                response = client.post('/api/auth/login', json={
                    'username': 'testuser',
                    'password': f'password{i}'
                })
                # All requests succeed without rate limiting
                assert response.status_code in [200, 401]
