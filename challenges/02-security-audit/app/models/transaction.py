from app import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    
    transaction_type = db.Column(db.String(20), nullable=False)  # debit, credit, transfer
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(50), unique=True)
    
    # SECURITY ISSUE: Recipient details not encrypted
    recipient_account = db.Column(db.String(20))
    recipient_name = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, reversed
    
    # SECURITY ISSUE: IP address logged but not used for fraud detection
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'currency': self.currency,
            'description': self.description,
            'reference_number': self.reference_number,
            'recipient_account': self.recipient_account,
            'recipient_name': self.recipient_name,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
