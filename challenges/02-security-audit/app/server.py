import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import bcrypt
import jwt
import hashlib

app = Flask(__name__)

# SECURITY ISSUE: Weak secret key
app.config['SECRET_KEY'] = 'secret'

# SECURITY ISSUE: Overly permissive CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# SECURITY ISSUE: Database credentials hardcoded
DB_CONFIG = {
    'host': 'localhost',
    'database': 'paysecure',
    'user': 'admin',
    'password': 'admin123'  # SECURITY ISSUE: Weak password
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# SECURITY ISSUE: Weak password hashing (MD5)
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # SECURITY ISSUE: No input validation
        # SECURITY ISSUE: Using MD5 instead of bcrypt
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SECURITY ISSUE: SQL injection vulnerability
        query = f"INSERT INTO users (email, password_hash) VALUES ('{email}', '{password_hash}')"
        cur.execute(query)
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        # SECURITY ISSUE: Exposing detailed error messages
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No rate limiting on login
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SECURITY ISSUE: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE email = '{email}'"
        cur.execute(query)
        user = cur.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # SECURITY ISSUE: Timing attack vulnerability
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if user[2] != password_hash:  # password_hash is at index 2
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # SECURITY ISSUE: Token with no expiration
        token = jwt.encode({'user_id': user[0]}, app.config['SECRET_KEY'])
        
        cur.close()
        conn.close()
        
        return jsonify({'token': token, 'user_id': user[0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No authentication required
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT id, email, balance FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user:
            return jsonify({
                'id': user[0],
                'email': user[1],
                'balance': float(user[2])
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No ownership validation
@app.route('/api/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    try:
        # Any logged-in user can access any account!
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))
        account = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if account:
            return jsonify({
                'id': account[0],
                'user_id': account[1],
                'account_number': account[2],
                'balance': float(account[3])
            }), 200
        else:
            return jsonify({'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: No transaction integrity checks
@app.route('/api/transfers', methods=['POST'])
def create_transfer():
    try:
        data = request.json
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = float(data.get('amount'))
        
        # SECURITY ISSUE: No authentication check
        # SECURITY ISSUE: No input validation (negative amounts?)
        # SECURITY ISSUE: No race condition protection
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check balance
        cur.execute('SELECT balance FROM accounts WHERE id = %s', (from_account,))
        balance = cur.fetchone()[0]
        
        if balance < amount:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # SECURITY ISSUE: No transaction wrapping
        cur.execute('UPDATE accounts SET balance = balance - %s WHERE id = %s', (amount, from_account))
        cur.execute('UPDATE accounts SET balance = balance + %s WHERE id = %s', (amount, to_account))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # SECURITY ISSUE: Logging sensitive financial data
        print(f"Transfer: {from_account} -> {to_account}, Amount: ${amount}")
        
        return jsonify({'message': 'Transfer successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Storing credit card data (PCI-DSS violation!)
@app.route('/api/payments', methods=['POST'])
def process_payment():
    try:
        data = request.json
        card_number = data.get('card_number')  # SECURITY ISSUE: Plain text card number
        cvv = data.get('cvv')  # SECURITY ISSUE: Plain text CVV
        expiry = data.get('expiry')
        amount = float(data.get('amount'))
        
        # SECURITY ISSUE: No payment gateway tokenization
        # SECURITY ISSUE: Storing credit card data in database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # PCI-DSS VIOLATION: Never store CVV!
        cur.execute('''
            INSERT INTO payments (card_number, cvv, expiry, amount, status)
            VALUES (%s, %s, %s, %s, 'completed')
        ''', (card_number, cvv, expiry, amount))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Payment processed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Webhook with no signature validation
@app.route('/api/webhooks/payment', methods=['POST'])
def payment_webhook():
    # SECURITY ISSUE: Anyone can call this endpoint
    # SECURITY ISSUE: No webhook signature verification
    data = request.json
    
    # Process webhook data without validation
    print(f"Webhook received: {data}")
    
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    # SECURITY ISSUE: Debug mode in production
    # SECURITY ISSUE: Running on 0.0.0.0 exposes to network
    app.run(debug=True, host='0.0.0.0', port=5000)
