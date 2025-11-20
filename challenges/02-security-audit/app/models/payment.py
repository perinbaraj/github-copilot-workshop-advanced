from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))
    
    # SECURITY ISSUE: Payment method details stored unencrypted
    payment_method = db.Column(db.String(20))  # card, bank_transfer, crypto
    
    # SECURITY ISSUE: Card details stored in plain text - MAJOR VIOLATION
    card_number = db.Column(db.String(16))
    card_holder_name = db.Column(db.String(100))
    card_expiry = db.Column(db.String(5))  # MM/YY
    cvv = db.Column(db.String(4))  # SECURITY ISSUE: CVV stored - PCI DSS violation
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # SECURITY ISSUE: Gateway response stored with sensitive data
    gateway_response = db.Column(db.Text)
    gateway_transaction_id = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='pending')
    
    # SECURITY ISSUE: Webhook signature not verified
    webhook_signature = db.Column(db.String(255))
    webhook_received = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        # SECURITY ISSUE: Exposing full card details
        return {
            'id': self.id,
            'user_id': self.user_id,
            'payment_method': self.payment_method,
            'card_number': self.card_number,  # SECURITY ISSUE: Full card number exposed
            'card_holder_name': self.card_holder_name,
            'card_expiry': self.card_expiry,
            'cvv': self.cvv,  # SECURITY ISSUE: CVV exposed
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
