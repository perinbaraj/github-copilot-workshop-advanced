from app import db
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # SECURITY ISSUE: Account number not encrypted
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # SECURITY ISSUE: Routing number stored in plain text
    routing_number = db.Column(db.String(9))
    
    account_type = db.Column(db.String(20), default='checking')  # checking, savings
    balance = db.Column(db.Numeric(15, 2), default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    status = db.Column(db.String(20), default='active')  # active, suspended, closed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def to_dict(self):
        # SECURITY ISSUE: Exposing full account details
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_number': self.account_number,  # SECURITY ISSUE: Full account number exposed
            'routing_number': self.routing_number,  # SECURITY ISSUE: Routing number exposed
            'account_type': self.account_type,
            'balance': float(self.balance),
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
