from flask import Blueprint, request, jsonify
from app.models.payment import Payment
from app import db
import hmac
import hashlib

bp = Blueprint('webhooks', __name__)

# SECURITY ISSUE: No webhook signature verification
@bp.route('/webhooks/payment', methods=['POST'])
def payment_webhook():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No authentication - anyone can trigger this
        # SECURITY ISSUE: No signature verification
        # SECURITY ISSUE: No replay attack prevention
        
        event_type = data.get('event_type')
        payment_id = data.get('payment_id')
        status = data.get('status')
        gateway_transaction_id = data.get('gateway_transaction_id')
        
        # SECURITY ISSUE: No validation of webhook source
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # SECURITY ISSUE: No idempotency check - can process same webhook multiple times
        
        # Update payment status
        payment.status = status
        payment.gateway_transaction_id = gateway_transaction_id
        payment.webhook_received = True
        
        db.session.commit()
        
        # SECURITY ISSUE: Returning sensitive information
        return jsonify({
            'message': 'Webhook processed successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        # SECURITY ISSUE: Exposing internal errors
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Webhook endpoint with minimal validation
@bp.route('/webhooks/transaction-update', methods=['POST'])
def transaction_update_webhook():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No rate limiting
        # SECURITY ISSUE: No IP whitelisting
        
        transaction_id = data.get('transaction_id')
        new_status = data.get('status')
        
        # SECURITY ISSUE: Direct database update without validation
        from app.models.transaction import Transaction
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        transaction.status = new_status
        db.session.commit()
        
        return jsonify({'message': 'Transaction updated'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Signature verification function - but not enforced
def verify_webhook_signature(payload, signature, secret):
    # SECURITY ISSUE: Weak signature algorithm
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # SECURITY ISSUE: Timing attack vulnerable comparison
    return expected_signature == signature

@bp.route('/webhooks/account-status', methods=['POST'])
def account_status_webhook():
    try:
        data = request.get_json()
        signature = request.headers.get('X-Webhook-Signature')
        
        # SECURITY ISSUE: Signature check commented out
        # if not verify_webhook_signature(str(data), signature, 'webhook-secret'):
        #     return jsonify({'error': 'Invalid signature'}), 401
        
        account_id = data.get('account_id')
        new_status = data.get('status')
        
        from app.models.account import Account
        account = Account.query.get(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: No notification to account owner
        account.status = new_status
        db.session.commit()
        
        return jsonify({'message': 'Account status updated'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
