from app.models.payment import Payment
from app.models.transaction import Transaction
from app import db
import requests
import time

# SECURITY ISSUE: Hardcoded payment gateway credentials
PAYMENT_GATEWAY_URL = 'https://api.paymentgateway.com/v1/charge'
GATEWAY_API_KEY = 'pk_test_1234567890'  # SECURITY ISSUE: API key in code
GATEWAY_SECRET = 'sk_test_0987654321'  # SECURITY ISSUE: Secret in code

def process_payment(user_id, transaction_id, payment_data):
    """
    Process a payment for a transaction
    
    SECURITY ISSUES:
    - No input validation
    - Storing sensitive card data
    - No encryption
    - Synchronous processing
    """
    
    try:
        # SECURITY ISSUE: No validation of payment data
        card_number = payment_data.get('card_number')
        card_holder = payment_data.get('card_holder_name')
        card_expiry = payment_data.get('card_expiry')
        cvv = payment_data.get('cvv')
        amount = payment_data.get('amount')
        
        # SECURITY ISSUE: Storing full card details - PCI DSS violation
        payment = Payment(
            user_id=user_id,
            transaction_id=transaction_id,
            payment_method='card',
            card_number=card_number,  # SECURITY ISSUE: Storing full card number
            card_holder_name=card_holder,
            card_expiry=card_expiry,
            cvv=cvv,  # SECURITY ISSUE: Storing CVV - major PCI DSS violation
            amount=amount,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # SECURITY ISSUE: Sending sensitive data to external API without encryption
        # SECURITY ISSUE: No retry logic
        # SECURITY ISSUE: No timeout configuration
        response = requests.post(
            PAYMENT_GATEWAY_URL,
            json={
                'card_number': card_number,
                'card_holder': card_holder,
                'card_expiry': card_expiry,
                'cvv': cvv,
                'amount': amount,
                'currency': 'USD'
            },
            headers={
                'Authorization': f'Bearer {GATEWAY_SECRET}'
            }
        )
        
        if response.status_code == 200:
            gateway_data = response.json()
            
            # SECURITY ISSUE: Storing gateway response with sensitive data
            payment.gateway_response = str(gateway_data)
            payment.gateway_transaction_id = gateway_data.get('transaction_id')
            payment.status = 'completed'
            
            # Update transaction status
            transaction = Transaction.query.get(transaction_id)
            if transaction:
                transaction.status = 'completed'
            
            db.session.commit()
            
            return {
                'success': True,
                'payment_id': payment.id,
                'transaction_id': gateway_data.get('transaction_id')
            }
        else:
            # SECURITY ISSUE: Exposing error details
            payment.status = 'failed'
            payment.gateway_response = response.text
            db.session.commit()
            
            return {
                'success': False,
                'error': response.text  # SECURITY ISSUE: Exposing internal errors
            }
            
    except Exception as e:
        # SECURITY ISSUE: Generic error handling
        # SECURITY ISSUE: No proper rollback
        return {
            'success': False,
            'error': str(e)  # SECURITY ISSUE: Exposing stack traces
        }

def refund_payment(payment_id, amount=None):
    """
    Process a refund
    
    SECURITY ISSUES:
    - No authorization check
    - No audit logging
    """
    
    payment = Payment.query.get(payment_id)
    if not payment:
        return {'success': False, 'error': 'Payment not found'}
    
    # SECURITY ISSUE: No authorization check - anyone can refund
    
    refund_amount = amount or payment.amount
    
    # SECURITY ISSUE: No validation of refund amount
    # SECURITY ISSUE: No check if already refunded
    
    try:
        response = requests.post(
            f'{PAYMENT_GATEWAY_URL}/refund',
            json={
                'transaction_id': payment.gateway_transaction_id,
                'amount': float(refund_amount)
            },
            headers={
                'Authorization': f'Bearer {GATEWAY_SECRET}'
            }
        )
        
        if response.status_code == 200:
            payment.status = 'refunded'
            db.session.commit()
            
            # SECURITY ISSUE: No notification to user
            
            return {'success': True, 'refund_amount': float(refund_amount)}
        else:
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_payment_status(payment_id):
    """
    Get payment status from gateway
    
    SECURITY ISSUE: No authorization check
    """
    
    payment = Payment.query.get(payment_id)
    if not payment:
        return None
    
    # SECURITY ISSUE: Returning full payment details including card info
    return payment.to_dict()

def validate_card(card_number):
    """
    Validate card number using Luhn algorithm
    
    SECURITY ISSUE: Not implemented - no validation
    """
    # SECURITY ISSUE: Card validation not implemented
    return True

def tokenize_card(card_data):
    """
    Tokenize card data
    
    SECURITY ISSUE: Not implemented - storing raw card data instead
    """
    # SECURITY ISSUE: Tokenization not implemented
    return card_data
