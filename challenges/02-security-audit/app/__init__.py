from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # SECURITY ISSUE: Debug mode enabled in production
    app.config['DEBUG'] = True
    
    # SECURITY ISSUE: Weak secret key
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key-123')
    
    # SECURITY ISSUE: SQL injection vulnerable - using string concatenation
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///paysecure.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SECURITY ISSUE: CORS misconfigured - allows all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # SECURITY ISSUE: No CSRF protection enabled
    
    # SECURITY ISSUE: Session cookies not secure
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = None
    
    # SECURITY ISSUE: No rate limiting
    
    db.init_app(app)
    
    # Register blueprints
    from app.api import transactions, accounts, webhooks
    from app.auth import auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(transactions.bp, url_prefix='/api')
    app.register_blueprint(accounts.bp, url_prefix='/api')
    app.register_blueprint(webhooks.bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
    
    return app
