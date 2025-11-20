from flask import Blueprint, request, jsonify
from app.models.transaction import Transaction
from app.models.account import Account
from app import db
from app.api.decorators import token_required
from datetime import datetime

bp = Blueprint('transactions', __name__)

# SECURITY ISSUE: SQL Injection vulnerability
@bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions():
    try:
        # SECURITY ISSUE: No pagination
        user_id = request.current_user.id
        
        # SECURITY ISSUE: SQL injection via raw query
        query = request.args.get('query', '')
        if query:
            # SECURITY ISSUE: String concatenation in SQL query
            sql = f"SELECT * FROM transactions WHERE user_id = {user_id} AND description LIKE '%{query}%'"
            transactions = db.session.execute(sql).fetchall()
        else:
            transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        return jsonify([t.to_dict() for t in transactions]), 200
        
    except Exception as e:
        # SECURITY ISSUE: Exposing internal errors
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: IDOR vulnerability
@bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(transaction_id):
    try:
        # SECURITY ISSUE: No ownership check - IDOR vulnerability
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # SECURITY ISSUE: Returning full transaction details without authorization
        return jsonify(transaction.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/create', methods=['POST'])
@token_required
def create_transaction():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input validation
        account_id = data.get('account_id')
        transaction_type = data.get('transaction_type')
        amount = data.get('amount')
        description = data.get('description')
        recipient_account = data.get('recipient_account')
        
        # SECURITY ISSUE: No ownership check for account
        account = Account.query.get(account_id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # SECURITY ISSUE: No balance validation for debit transactions
        # SECURITY ISSUE: No fraud detection
        # SECURITY ISSUE: No transaction limits
        
        transaction = Transaction(
            user_id=request.current_user.id,
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            recipient_account=recipient_account,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status='completed'  # SECURITY ISSUE: No approval workflow
        )
        
        # Update account balance
        if transaction_type == 'debit':
            account.balance -= amount
        elif transaction_type == 'credit':
            account.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Mass assignment vulnerability
@bp.route('/transactions/<int:transaction_id>/update', methods=['PUT'])
@token_required
def update_transaction(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # SECURITY ISSUE: No ownership check
        
        data = request.get_json()
        
        # SECURITY ISSUE: Mass assignment - allows updating any field
        for key, value in data.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No authorization for deletion
@bp.route('/transactions/<int:transaction_id>/delete', methods=['DELETE'])
@token_required
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # SECURITY ISSUE: No ownership check
        # SECURITY ISSUE: No audit trail for deletion
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No rate limiting on search
@bp.route('/transactions/search', methods=['GET'])
@token_required
def search_transactions():
    try:
        search_term = request.args.get('q', '')
        
        # SECURITY ISSUE: SQL injection via search parameter
        sql = f"""
        SELECT * FROM transactions 
        WHERE user_id = {request.current_user.id} 
        AND (description LIKE '%{search_term}%' OR recipient_name LIKE '%{search_term}%')
        """
        
        transactions = db.session.execute(sql).fetchall()
        
        return jsonify([dict(t) for t in transactions]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
