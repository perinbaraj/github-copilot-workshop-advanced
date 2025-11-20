import os

class Config:
    # SECURITY ISSUE: Hardcoded credentials
    SECRET_KEY = 'super-secret-key-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///paysecure.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SECURITY ISSUE: Debug mode enabled
    DEBUG = True
    
    # SECURITY ISSUE: Weak JWT settings
    JWT_SECRET_KEY = 'jwt-secret'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 720  # SECURITY ISSUE: Token never expires (30 days)
    
    # SECURITY ISSUE: Insecure session configuration
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    PERMANENT_SESSION_LIFETIME = 86400 * 365  # SECURITY ISSUE: 1 year session
    
    # SECURITY ISSUE: Weak password requirements
    MIN_PASSWORD_LENGTH = 4
    REQUIRE_UPPERCASE = False
    REQUIRE_NUMBERS = False
    REQUIRE_SPECIAL_CHARS = False
    
    # SECURITY ISSUE: Weak bcrypt rounds
    BCRYPT_LOG_ROUNDS = 4
    
    # SECURITY ISSUE: No rate limiting
    RATELIMIT_ENABLED = False
    
    # SECURITY ISSUE: Payment gateway credentials exposed
    PAYMENT_GATEWAY_API_KEY = 'pk_test_1234567890'
    PAYMENT_GATEWAY_SECRET = 'sk_test_0987654321'
    
    # SECURITY ISSUE: SMTP credentials hardcoded
    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'paysecure@example.com'
    SMTP_PASSWORD = 'EmailPassword123!'
    
    # SECURITY ISSUE: Encryption key stored in config
    ENCRYPTION_KEY = 'this-is-a-very-weak-encryption-key-32'
    
    # SECURITY ISSUE: No Content Security Policy
    CSP_ENABLED = False
    
    # SECURITY ISSUE: Audit logging disabled
    AUDIT_LOGGING = False
    
    # SECURITY ISSUE: MFA disabled by default
    MFA_REQUIRED = False
    MFA_ISSUER = 'PaySecure'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # SECURITY ISSUE: SQL queries logged

class ProductionConfig(Config):
    # SECURITY ISSUE: Production config still has debug enabled
    DEBUG = True  # Should be False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
