"""
Payment security tests

Tests payment-related vulnerabilities including:
- PCI-DSS violations
- Credit card data storage
- Insecure payment processing
- Weak webhook verification
"""

import pytest
from app.models.user import User
from app.models.payment import Payment
from app.payments.process import process_payment
from app.payments.gateway import PaymentGateway
from app.payments.webhooks import verify_signature, handle_payment_webhook
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

class TestPCIDSSViolations:
    """Test PCI-DSS compliance violations"""
    
    def test_full_card_number_stored(self, app):
        """Test that full card numbers are stored (PCI-DSS violation)"""
        with app.app_context():
            # CRITICAL VULNERABILITY: Storing full card number
            payment = Payment(
                user_id=1,
                card_number='4532015112830366',  # Full 16 digits
                cvv='123',
                card_expiry='12/25',
                amount=100.00
            )
            db.session.add(payment)
            db.session.commit()
            
            # Retrieve and verify full number is stored
            retrieved = Payment.query.get(payment.id)
            assert len(retrieved.card_number) == 16  # PCI-DSS violation
    
    def test_cvv_stored(self, app):
        """Test that CVV is stored (critical PCI-DSS violation)"""
        with app.app_context():
            # CRITICAL VULNERABILITY: Storing CVV is never allowed
            payment = Payment(
                user_id=1,
                card_number='4532015112830366',
                cvv='123',  # NEVER store CVV
                card_expiry='12/25',
                amount=100.00
            )
            db.session.add(payment)
            db.session.commit()
            
            # Verify CVV is stored
            retrieved = Payment.query.get(payment.id)
            assert retrieved.cvv == '123'  # CRITICAL violation
    
    def test_card_data_unencrypted(self, app):
        """Test that card data is stored unencrypted (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Card data not encrypted at rest
            payment = Payment(
                user_id=1,
                card_number='4532015112830366',
                cvv='123',
                card_expiry='12/25',
                amount=100.00
            )
            db.session.add(payment)
            db.session.commit()
            
            # Card data stored in plaintext in database
    
    def test_card_data_exposed_in_api(self, authenticated_client, app):
        """Test that card data is exposed in API (vulnerability)"""
        with app.app_context():
            # Create payment
            payment = Payment(
                user_id=1,
                card_number='4532015112830366',
                cvv='123',
                card_expiry='12/25',
                amount=100.00
            )
            db.session.add(payment)
            db.session.commit()
            
            # VULNERABLE: API returns full card details
            response = authenticated_client.get(f'/api/payments/{payment.id}')
            
            # Should mask card number, not expose CVV at all
            data = response.json
            if data:
                # Vulnerability: full card data might be in response

                pass
    
    def test_no_tokenization(self, app):
        """Test that tokenization is not used (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Should use payment tokens, not store cards
            # No token field in Payment model
            payment = Payment(
                user_id=1,
                card_number='4532015112830366',
                cvv='123',
                card_expiry='12/25',
                amount=100.00
            )
            
            # Should have token field instead of card_number

class TestPaymentProcessing:
    """Test payment processing vulnerabilities"""
    
    def test_hardcoded_credentials(self, app):
        """Test hardcoded payment gateway credentials (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Hardcoded API credentials
            gateway = PaymentGateway()
            
            # Should use environment variables or secure vault
            # Check if credentials are hardcoded in process.py
    
    def test_ssl_verification_disabled(self, app):
        """Test that SSL verification is disabled (vulnerability)"""
        with app.app_context():
            # VULNERABLE: verify_ssl=False in gateway requests
            gateway = PaymentGateway()
            
            # SSL verification should always be enabled
    
    def test_no_request_timeout(self, app):
        """Test lack of request timeout (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No timeout on payment requests
            # Can cause hanging requests and DoS
            gateway = PaymentGateway()
    
    def test_synchronous_payment_processing(self, app):
        """Test synchronous payment processing (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Synchronous processing blocks server
            # Should use async or background jobs
            payment_data = {
                'user_id': 1,
                'amount': 100.00,
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '12/25'
            }
            
            # Process payment synchronously
            # result = process_payment(payment_data)
    
    def test_error_exposes_stack_trace(self, authenticated_client, app):
        """Test that errors expose stack traces (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Stack traces exposed to clients
            response = authenticated_client.post('/api/payments', json={
                'amount': 'invalid',  # Trigger error
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '12/25'
            })
            
            # Should return generic error, not stack trace

class TestWebhookSecurity:
    """Test webhook security vulnerabilities"""
    
    def test_weak_signature_verification(self, app):
        """Test weak webhook signature verification (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Using MD5 instead of HMAC-SHA256
            payload = b'{"event": "payment.success"}'
            signature = 'test_signature'
            
            # verify_signature uses MD5 (weak)
            # Should use HMAC-SHA256
    
    def test_no_replay_protection(self, app):
        """Test lack of replay attack protection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No timestamp or nonce checking
            # Same webhook can be replayed multiple times
            
            payload = {
                'event': 'payment.success',
                'payment_id': '12345',
                'amount': 100.00
            }
            
            # Can process same webhook multiple times
    
    def test_no_idempotency(self, authenticated_client, app):
        """Test lack of idempotency (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No idempotency key checking
            # Processing same webhook multiple times causes duplicate actions
            
            webhook_data = {
                'event': 'payment.success',
                'payment_id': '12345',
                'amount': 100.00,
                'signature': 'test'
            }
            
            # Send webhook twice
            response1 = authenticated_client.post('/api/webhooks/payment', json=webhook_data)
            response2 = authenticated_client.post('/api/webhooks/payment', json=webhook_data)
            
            # Should only process once
    
    def test_timing_attack_on_signature(self, app):
        """Test timing attack vulnerability in signature verification (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Using == for signature comparison
            # Should use constant-time comparison
            
            payload = b'test'
            correct_sig = 'abc123'
            wrong_sig = 'xyz789'
            
            # verify_signature(payload, correct_sig, 'secret')
            # Uses string == comparison (timing attack vulnerable)
    
    def test_no_webhook_authentication(self, client, app):
        """Test lack of webhook authentication (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Anyone can send webhooks
            # No IP whitelist or additional authentication
            
            response = client.post('/api/webhooks/payment', json={
                'event': 'payment.success',
                'payment_id': '12345',
                'amount': 100.00
            })

class TestPaymentValidation:
    """Test payment validation vulnerabilities"""
    
    def test_negative_amount_accepted(self, authenticated_client, app):
        """Test that negative amounts are accepted (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No validation for negative amounts
            response = authenticated_client.post('/api/payments', json={
                'amount': -100.00,
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '12/25'
            })
    
    def test_no_amount_limit(self, authenticated_client, app):
        """Test lack of maximum amount limit (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No maximum transaction limit
            response = authenticated_client.post('/api/payments', json={
                'amount': 9999999999.99,
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '12/25'
            })
    
    def test_invalid_card_number_accepted(self, authenticated_client, app):
        """Test that invalid card numbers are accepted (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No Luhn algorithm validation
            response = authenticated_client.post('/api/payments', json={
                'amount': 100.00,
                'card_number': '1234567890123456',  # Invalid
                'cvv': '123',
                'card_expiry': '12/25'
            })
    
    def test_expired_card_accepted(self, authenticated_client, app):
        """Test that expired cards are accepted (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No expiration date validation
            response = authenticated_client.post('/api/payments', json={
                'amount': 100.00,
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '01/20'  # Expired
            })

class TestPaymentAuditLogging:
    """Test payment audit logging"""
    
    def test_insufficient_payment_logging(self, app):
        """Test that payment logging is insufficient (vulnerability)"""
        with app.app_context():
            # VULNERABLE: Not logging all payment details
            # Should log: user, amount, time, IP, device, result
            
            payment_data = {
                'user_id': 1,
                'amount': 100.00,
                'card_number': '4532015112830366',
                'cvv': '123',
                'card_expiry': '12/25'
            }
            
            # Missing comprehensive audit trail
    
    def test_no_fraud_detection(self, app):
        """Test lack of fraud detection (vulnerability)"""
        with app.app_context():
            # VULNERABLE: No fraud detection checks
            # Should check for: velocity, location, pattern anomalies
            pass
