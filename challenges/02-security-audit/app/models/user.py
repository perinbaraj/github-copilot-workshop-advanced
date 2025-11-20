from app import db
from datetime import datetime
import hashlib

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # SECURITY ISSUE: Password stored with weak hashing (MD5)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # SECURITY ISSUE: Sensitive data not encrypted
    ssn = db.Column(db.String(11))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    
    # SECURITY ISSUE: MFA secret stored in plain text
    mfa_secret = db.Column(db.String(32))
    mfa_enabled = db.Column(db.Boolean, default=False)
    
    # SECURITY ISSUE: Password reset token not hashed
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = db.relationship('Account', backref='owner', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        # SECURITY ISSUE: Using MD5 instead of bcrypt/argon2
        self.password_hash = hashlib.md5(password.encode()).hexdigest()
    
    def check_password(self, password):
        # SECURITY ISSUE: Timing attack vulnerable
        return self.password_hash == hashlib.md5(password.encode()).hexdigest()
    
    def to_dict(self):
        # SECURITY ISSUE: Exposing sensitive information
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'ssn': self.ssn,  # SECURITY ISSUE: SSN exposed
            'phone': self.phone,
            'role': self.role,
            'mfa_secret': self.mfa_secret,  # SECURITY ISSUE: MFA secret exposed
            'created_at': self.created_at.isoformat()
        }
