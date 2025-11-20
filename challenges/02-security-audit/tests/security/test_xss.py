"""
XSS (Cross-Site Scripting) security tests

Tests XSS vulnerabilities including:
- Reflected XSS
- Stored XSS
- DOM-based XSS
- XSS in different contexts
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

class TestReflectedXSS:
    """Test reflected XSS vulnerabilities"""
    
    def test_xss_in_search_parameter(self, authenticated_client, app):
        """Test XSS in search query parameter (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Search term reflected without sanitization
            xss_payload = '<script>alert("XSS")</script>'
            
            response = authenticated_client.get(
                f'/api/transactions/search?query={xss_payload}'
            )
            
            # Vulnerability: payload might be reflected in response
            # Should be HTML-encoded
    
    def test_xss_in_error_message(self, client, app):
        """Test XSS in error messages (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Error messages reflect user input
            xss_payload = '<img src=x onerror=alert("XSS")>'
            
            response = client.post('/api/auth/login', json={
                'username': xss_payload,
                'password': 'test'
            })
            
            # Vulnerability: username might appear in error without encoding
    
    def test_xss_in_redirect(self, client, app):
        """Test XSS in redirect parameter (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Redirect URL not validated
            xss_payload = 'javascript:alert("XSS")'
            
            response = client.get(f'/redirect?url={xss_payload}')
            
            # Vulnerability: might execute JavaScript

class TestStoredXSS:
    """Test stored (persistent) XSS vulnerabilities"""
    
    def test_xss_in_transaction_description(self, authenticated_client, app):
        """Test stored XSS in transaction description (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Transaction description not sanitized
            xss_payload = '<script>alert(document.cookie)</script>'
            
            response = authenticated_client.post('/api/transactions', json={
                'amount': 100,
                'description': xss_payload,
                'account_id': 1
            })
            
            # Vulnerability: XSS stored in database
            # Will execute when transaction is viewed
            
            # Retrieve transaction
            response = authenticated_client.get('/api/transactions/1')
            # Payload should be in response
    
    def test_xss_in_user_profile(self, authenticated_client, app):
        """Test stored XSS in user profile (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Profile fields not sanitized
            xss_payload = '<img src=x onerror=alert("XSS")>'
            
            response = authenticated_client.put('/api/users/me', json={
                'full_name': xss_payload,
                'phone': '1234567890'
            })
            
            # Vulnerability: XSS stored in user profile
            
            # Retrieve profile
            response = authenticated_client.get('/api/users/me')
            # Payload should be in response
    
    def test_xss_in_comment_field(self, authenticated_client, app):
        """Test stored XSS in comments (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Comments not sanitized
            xss_payload = '<svg/onload=alert("XSS")>'
            
            # If comments feature exists
            # response = authenticated_client.post('/api/transactions/1/comments', json={
            #     'comment': xss_payload
            # })

class TestDOMBasedXSS:
    """Test DOM-based XSS vulnerabilities"""
    
    def test_xss_in_client_side_rendering(self, client, app):
        """Test DOM-based XSS in client-side code (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Client-side JavaScript uses unescaped data
            # Example: document.getElementById('output').innerHTML = userInput
            
            # This would be in frontend JavaScript, documenting the risk
            pass
    
    def test_xss_via_location_hash(self, client, app):
        """Test XSS via location.hash (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Using window.location.hash without sanitization
            # Example URL: #<img src=x onerror=alert("XSS")>
            pass

class TestXSSInDifferentContexts:
    """Test XSS in various contexts"""
    
    def test_xss_in_html_context(self, authenticated_client, app):
        """Test XSS in HTML context (vulnerability)"""
        with app.app_context():
            xss_payload = '<b onmouseover=alert("XSS")>test</b>'
            
            response = authenticated_client.post('/api/transactions', json={
                'amount': 100,
                'description': xss_payload,
                'account_id': 1
            })
    
    def test_xss_in_attribute_context(self, authenticated_client, app):
        """Test XSS in HTML attribute (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Data used in HTML attributes
            xss_payload = '" onload="alert("XSS")'
            
            response = authenticated_client.put('/api/users/me', json={
                'full_name': xss_payload
            })
    
    def test_xss_in_javascript_context(self, authenticated_client, app):
        """Test XSS in JavaScript context (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Data embedded in JavaScript code
            xss_payload = '</script><script>alert("XSS")</script>'
            
            response = authenticated_client.get(f'/api/search?q={xss_payload}')
    
    def test_xss_in_css_context(self, authenticated_client, app):
        """Test XSS in CSS context (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Data used in CSS
            xss_payload = 'expression(alert("XSS"))'
            
            # If custom CSS is allowed
            pass

class TestXSSBypass:
    """Test XSS filter bypass techniques"""
    
    def test_xss_with_encoding(self, authenticated_client, app):
        """Test XSS with various encodings (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Encoding bypasses
            payloads = [
                '&#60;script&#62;alert("XSS")&#60;/script&#62;',  # HTML entities
                '%3Cscript%3Ealert("XSS")%3C/script%3E',  # URL encoding
                '\u003cscript\u003ealert("XSS")\u003c/script\u003e',  # Unicode
            ]
            
            for payload in payloads:
                response = authenticated_client.post('/api/transactions', json={
                    'amount': 100,
                    'description': payload,
                    'account_id': 1
                })
    
    def test_xss_with_uppercase(self, authenticated_client, app):
        """Test XSS with case variations (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Case-insensitive bypass
            payloads = [
                '<SCRIPT>alert("XSS")</SCRIPT>',
                '<ScRiPt>alert("XSS")</sCrIpT>',
            ]
            
            for payload in payloads:
                response = authenticated_client.post('/api/transactions', json={
                    'amount': 100,
                    'description': payload,
                    'account_id': 1
                })
    
    def test_xss_with_null_bytes(self, authenticated_client, app):
        """Test XSS with null byte injection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Null byte bypass
            xss_payload = '<scr\x00ipt>alert("XSS")</scr\x00ipt>'
            
            response = authenticated_client.post('/api/transactions', json={
                'amount': 100,
                'description': xss_payload,
                'account_id': 1
            })

class TestContentSecurityPolicy:
    """Test Content Security Policy implementation"""
    
    def test_missing_csp_header(self, client, app):
        """Test missing CSP header (vulnerability)"""
        with app.app_context():
            response = client.get('/')
            
            # VULNERABLE: No CSP header or weak CSP
            csp_header = response.headers.get('Content-Security-Policy')
            
            # Should have strict CSP like:
            # default-src 'self'; script-src 'self'; object-src 'none'
    
    def test_weak_csp_header(self, client, app):
        """Test weak CSP that allows unsafe-inline (vulnerability)"""
        with app.app_context():
            response = client.get('/')
            
            csp_header = response.headers.get('Content-Security-Policy', '')
            
            # VULNERABLE: CSP allows 'unsafe-inline' or 'unsafe-eval'
            assert 'unsafe-inline' in csp_header or 'unsafe-eval' in csp_header

class TestInputSanitization:
    """Test input sanitization"""
    
    def test_no_html_escaping(self, authenticated_client, app):
        """Test that HTML is not escaped (vulnerability)"""
        with app.app_context():
            # VULNERABLE: HTML not escaped in output
            html_input = '<b>Bold Text</b>'
            
            response = authenticated_client.post('/api/transactions', json={
                'amount': 100,
                'description': html_input,
                'account_id': 1
            })
            
            # Retrieve and check if HTML is escaped
            response = authenticated_client.get('/api/transactions/1')
            # Should be escaped as &lt;b&gt;Bold Text&lt;/b&gt;
    
    def test_incomplete_sanitization(self, authenticated_client, app):
        """Test incomplete input sanitization (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Sanitization removes <script> but not other vectors
            xss_payloads = [
                '<img src=x onerror=alert("XSS")>',
                '<svg/onload=alert("XSS")>',
                '<iframe src="javascript:alert(\'XSS\')">',
            ]
            
            for payload in xss_payloads:
                response = authenticated_client.post('/api/transactions', json={
                    'amount': 100,
                    'description': payload,
                    'account_id': 1
                })
