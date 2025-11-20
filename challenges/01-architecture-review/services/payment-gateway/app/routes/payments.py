from flask import Blueprint, request, jsonify, current_app
import psycopg2
import random
import time

bp = Blueprint('payments', __name__, url_prefix='/payments')

def get_db_connection():
    # PERFORMANCE ISSUE: Creating new connection for each request
    conn = psycopg2.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        database=current_app.config['DB_NAME'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD']
    )
    return conn

@bp.route('/process', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()
        
        # SECURITY ISSUE: No input validation
        order_id = data.get('orderId')
        amount = data.get('amount')
        user_id = data.get('userId')
        
        # SECURITY ISSUE: No authentication/authorization
        
        # PERFORMANCE ISSUE: Synchronous payment processing
        # Simulate payment gateway call
        time.sleep(2)  # PERFORMANCE ISSUE: Blocking I/O
        
        # Simulate random payment failures
        if random.random() < 0.1:  # 10% failure rate
            return jsonify({'error': 'Payment declined'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SECURITY ISSUE: Sensitive payment info stored without encryption
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'completed',
                transaction_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        transaction_id = f'TXN-{order_id}-{int(time.time())}'
        
        cursor.execute(
            'INSERT INTO payments (order_id, user_id, amount, transaction_id) VALUES (%s, %s, %s, %s) RETURNING id',
            (order_id, user_id, amount, transaction_id)
        )
        
        payment_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # ARCHITECTURE ISSUE: No webhook verification
        # ARCHITECTURE ISSUE: No retry logic
        
        return jsonify({
            'paymentId': payment_id,
            'transactionId': transaction_id,
            'status': 'completed'
        }), 200
        
    except Exception as e:
        # CODE QUALITY ISSUE: Generic error handling
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SECURITY ISSUE: No authorization check
        cursor.execute('SELECT * FROM payments WHERE id = %s', (payment_id,))
        
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'id': row[0],
            'orderId': row[1],
            'userId': row[2],
            'amount': float(row[3]),
            'status': row[4],
            'transactionId': row[5],
            'createdAt': str(row[6])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SECURITY ISSUE: Webhook endpoint with no signature verification
@bp.route('/webhook', methods=['POST'])
def payment_webhook():
    data = request.get_json()
    
    # SECURITY ISSUE: No verification of webhook authenticity
    # Anyone can call this endpoint
    
    # Process webhook data
    return jsonify({'status': 'received'}), 200
