import requests
from datetime import datetime, timedelta

class PaymentGateway:
    """
    Payment gateway integration
    
    SECURITY ISSUES:
    - Hardcoded credentials
    - No encryption
    - No proper error handling
    - No retry logic
    """
    
    def __init__(self):
        # SECURITY ISSUE: Hardcoded credentials
        self.api_key = 'pk_test_1234567890'
        self.secret_key = 'sk_test_0987654321'
        self.base_url = 'https://api.paymentgateway.com/v1'
        
        # SECURITY ISSUE: No SSL certificate verification
        self.verify_ssl = False
    
    def create_charge(self, amount, currency, card_data, customer_id=None):
        """
        Create a charge
        
        SECURITY ISSUES:
        - No input validation
        - Sending sensitive data unencrypted
        - No idempotency key
        """
        
        # SECURITY ISSUE: No amount validation
        # SECURITY ISSUE: No currency validation
        
        payload = {
            'amount': amount,
            'currency': currency,
            'source': {
                'card_number': card_data.get('card_number'),
                'exp_month': card_data.get('exp_month'),
                'exp_year': card_data.get('exp_year'),
                'cvc': card_data.get('cvc')
            }
        }
        
        if customer_id:
            payload['customer'] = customer_id
        
        # SECURITY ISSUE: No timeout
        # SECURITY ISSUE: SSL verification disabled
        response = requests.post(
            f'{self.base_url}/charges',
            json=payload,
            auth=(self.secret_key, ''),
            verify=self.verify_ssl
        )
        
        # SECURITY ISSUE: No status code validation
        return response.json()
    
    def create_refund(self, charge_id, amount=None):
        """
        Create a refund
        
        SECURITY ISSUE: No validation
        """
        
        payload = {'charge': charge_id}
        if amount:
            payload['amount'] = amount
        
        response = requests.post(
            f'{self.base_url}/refunds',
            json=payload,
            auth=(self.secret_key, ''),
            verify=self.verify_ssl
        )
        
        return response.json()
    
    def retrieve_charge(self, charge_id):
        """
        Retrieve charge details
        
        SECURITY ISSUE: No authorization
        """
        
        response = requests.get(
            f'{self.base_url}/charges/{charge_id}',
            auth=(self.secret_key, ''),
            verify=self.verify_ssl
        )
        
        return response.json()
    
    def create_customer(self, email, card_data):
        """
        Create a customer with saved card
        
        SECURITY ISSUE: Storing card data
        """
        
        payload = {
            'email': email,
            'source': {
                'card_number': card_data.get('card_number'),
                'exp_month': card_data.get('exp_month'),
                'exp_year': card_data.get('exp_year'),
                'cvc': card_data.get('cvc')
            }
        }
        
        response = requests.post(
            f'{self.base_url}/customers',
            json=payload,
            auth=(self.secret_key, ''),
            verify=self.verify_ssl
        )
        
        return response.json()
    
    def verify_webhook_signature(self, payload, signature, timestamp):
        """
        Verify webhook signature
        
        SECURITY ISSUE: Not implemented properly
        """
        
        # SECURITY ISSUE: Signature verification not implemented
        # Just returns True without checking
        return True
    
    def handle_webhook(self, event_type, data):
        """
        Handle webhook events
        
        SECURITY ISSUES:
        - No signature verification
        - No replay attack prevention
        - No idempotency check
        """
        
        # SECURITY ISSUE: Processing webhook without verification
        
        if event_type == 'charge.succeeded':
            # Update payment status
            pass
        elif event_type == 'charge.failed':
            # Handle failed payment
            pass
        elif event_type == 'refund.created':
            # Handle refund
            pass
        
        # SECURITY ISSUE: No return value validation
        return {'received': True}
