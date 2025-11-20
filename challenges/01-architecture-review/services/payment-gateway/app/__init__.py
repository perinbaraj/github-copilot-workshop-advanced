from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    
    # SECURITY ISSUE: Debug mode enabled
    app.config['DEBUG'] = True
    
    # SECURITY ISSUE: Weak secret key
    app.config['SECRET_KEY'] = 'insecure-secret-key'
    
    # Database configuration
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'postgres')
    app.config['DB_PORT'] = os.getenv('DB_PORT', '5432')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'techmart')
    app.config['DB_USER'] = os.getenv('DB_USER', 'admin')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'password123')
    
    from .routes import payments
    app.register_blueprint(payments.bp)
    
    return app
