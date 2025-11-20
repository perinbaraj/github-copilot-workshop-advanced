from flask import request, jsonify
from app.models.payment import Payment
from app import db
import hmac
import hashlib
import time

# SECURITY ISSUE: Webhook secret hardcoded
WEBHOOK_SECRET = 'whsec_test_secret_key'

def handle_payment_webhook(data, signature):
    """
    Handle payment webhook from gateway
    
    SECURITY ISSUES:
    - Weak signature verification
    - No replay attack prevention
    - No rate limiting
    - Processing without proper validation
    """
    
    # SECURITY ISSUE: Signature verification can be bypassed
    if not verify_signature(data, signature):
        # SECURITY ISSUE: Still processes even if verification fails (commented out)
        # return {'error': 'Invalid signature'}, 401
        pass
    
    event_type = data.get('type')
    payment_data = data.get('data', {}).get('object', {})
    
    # SECURITY ISSUE: No event type validation
    # SECURITY ISSUE: No idempotency check - can process same event multiple times
    
    if event_type == 'payment.succeeded':
        return handle_payment_success(payment_data)
    elif event_type == 'payment.failed':
        return handle_payment_failure(payment_data)
    elif event_type == 'refund.created':
        return handle_refund_created(payment_data)
    else:
        # SECURITY ISSUE: Accepting unknown event types
        return {'received': True}, 200

def verify_signature(payload, signature):
    """
    Verify webhook signature
    
    SECURITY ISSUES:
    - Weak signature algorithm
    - Timing attack vulnerable
    - Secret key hardcoded
    """
    
    # SECURITY ISSUE: Using MD5 instead of HMAC-SHA256
    expected_signature = hashlib.md5(
        (str(payload) + WEBHOOK_SECRET).encode()
    ).hexdigest()
    
    # SECURITY ISSUE: Timing attack vulnerable comparison
    return expected_signature == signature

def handle_payment_success(payment_data):
    """
    Handle successful payment
    
    SECURITY ISSUES:
    - No validation of payment data
    - No user notification
    - No audit logging
    """
    
    gateway_transaction_id = payment_data.get('id')
    
    # SECURITY ISSUE: Direct database query without validation
    payment = Payment.query.filter_by(
        gateway_transaction_id=gateway_transaction_id
    ).first()
    
    if not payment:
        # SECURITY ISSUE: Creating new payment from webhook without validation
        payment = Payment(
            gateway_transaction_id=gateway_transaction_id,
            amount=payment_data.get('amount'),
            status='completed'
        )
        db.session.add(payment)
    else:
        payment.status = 'completed'
        payment.gateway_response = str(payment_data)
    
    db.session.commit()
    
    # SECURITY ISSUE: No notification to user
    # SECURITY ISSUE: No fraud detection
    
    return {'received': True}, 200

def handle_payment_failure(payment_data):
    """
    Handle failed payment
    
    SECURITY ISSUE: No proper error handling
    """
    
    gateway_transaction_id = payment_data.get('id')
    
    payment = Payment.query.filter_by(
        gateway_transaction_id=gateway_transaction_id
    ).first()
    
    if payment:
        payment.status = 'failed'
        payment.gateway_response = str(payment_data)
        db.session.commit()
    
    # SECURITY ISSUE: No user notification
    
    return {'received': True}, 200

def handle_refund_created(payment_data):
    """
    Handle refund creation
    
    SECURITY ISSUES:
    - No authorization check
    - No validation
    """
    
    charge_id = payment_data.get('charge')
    refund_amount = payment_data.get('amount')
    
    payment = Payment.query.filter_by(
        gateway_transaction_id=charge_id
    ).first()
    
    if payment:
        # SECURITY ISSUE: No check if refund amount is valid
        # SECURITY ISSUE: No check if already refunded
        payment.status = 'refunded'
        db.session.commit()
    
    # SECURITY ISSUE: No notification to user
    
    return {'received': True}, 200

def validate_webhook_timestamp(timestamp):
    """
    Validate webhook timestamp to prevent replay attacks
    
    SECURITY ISSUE: Not implemented
    """
    
    # SECURITY ISSUE: Timestamp validation not implemented
    # Should check if timestamp is within acceptable range (e.g., 5 minutes)
    return True

def check_idempotency(event_id):
    """
    Check if event was already processed
    
    SECURITY ISSUE: Not implemented
    """
    
    # SECURITY ISSUE: Idempotency check not implemented
    # Should track processed event IDs
    return False

def log_webhook_event(event_type, data, status):
    """
    Log webhook event for audit
    
    SECURITY ISSUE: Not implemented
    """
    
    # SECURITY ISSUE: Webhook events not logged
    # Should store all webhook events for audit trail
    pass
