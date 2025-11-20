from flask import Blueprint, request, jsonify
from app.models.account import Account
from app.models.transaction import Transaction
from app import db
from app.api.decorators import token_required
from datetime import datetime

bp = Blueprint('accounts', __name__)

# SECURITY ISSUE: IDOR vulnerability - no ownership validation
@bp.route('/accounts/<int:account_id>', methods=['GET'])
@token_required
def get_account(account_id):
    try:
        # SECURITY ISSUE: Direct object reference without ownership check
        account = Account.query.get(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: Returning sensitive account details
        return jsonify(account.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts', methods=['GET'])
@token_required
def get_accounts():
    try:
        # Only return accounts for current user
        accounts = Account.query.filter_by(user_id=request.current_user.id).all()
        
        return jsonify([account.to_dict() for account in accounts]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts/create', methods=['POST'])
@token_required
def create_account():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input validation
        account_type = data.get('account_type', 'checking')
        
        # SECURITY ISSUE: Predictable account number generation
        import random
        account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        routing_number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        account = Account(
            user_id=request.current_user.id,
            account_number=account_number,
            routing_number=routing_number,
            account_type=account_type,
            balance=0.0
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'account': account.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No authorization check
@bp.route('/accounts/<int:account_id>/balance', methods=['GET'])
@token_required
def get_balance(account_id):
    try:
        # SECURITY ISSUE: IDOR - anyone can check any account balance
        account = Account.query.get(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        return jsonify({
            'account_id': account.id,
            'balance': float(account.balance),
            'currency': account.currency
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Mass assignment vulnerability
@bp.route('/accounts/<int:account_id>/update', methods=['PUT'])
@token_required
def update_account(account_id):
    try:
        account = Account.query.get(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: No ownership check
        
        data = request.get_json()
        
        # SECURITY ISSUE: Mass assignment - allows updating sensitive fields
        for key, value in data.items():
            if hasattr(account, key):
                setattr(account, key, value)  # Can update balance, status, etc.
        
        db.session.commit()
        
        return jsonify({
            'message': 'Account updated successfully',
            'account': account.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No proper authorization
@bp.route('/accounts/<int:account_id>/transactions', methods=['GET'])
@token_required
def get_account_transactions(account_id):
    try:
        # SECURITY ISSUE: IDOR vulnerability
        account = Account.query.get(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: No pagination - can expose large datasets
        transactions = Transaction.query.filter_by(account_id=account_id).all()
        
        return jsonify([t.to_dict() for t in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Dangerous endpoint with no safeguards
@bp.route('/accounts/<int:account_id>/transfer', methods=['POST'])
@token_required
def transfer_funds(account_id):
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input validation
        recipient_account_id = data.get('recipient_account_id')
        amount = data.get('amount')
        
        # SECURITY ISSUE: No ownership check
        source_account = Account.query.get(account_id)
        recipient_account = Account.query.get(recipient_account_id)
        
        if not source_account or not recipient_account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: Race condition - no transaction locking
        # SECURITY ISSUE: No fraud detection
        # SECURITY ISSUE: No transfer limits
        
        if source_account.balance < amount:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Perform transfer
        source_account.balance -= amount
        recipient_account.balance += amount
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transfer successful',
            'source_balance': float(source_account.balance),
            'recipient_balance': float(recipient_account.balance)
        }), 200
        
    except Exception as e:
        # SECURITY ISSUE: Rollback not guaranteed
        return jsonify({'error': str(e)}), 500
