import secrets
from datetime import datetime, timedelta
from flask import request, jsonify
from app.auth import auth_bp
from app.models.user import User
from app import db
import smtplib
from email.mime.text import MIMEText

# SECURITY ISSUE: Multiple password reset vulnerabilities

@auth_bp.route('/password/reset-request', methods=['POST'])
def request_password_reset():
    try:
        data = request.get_json()
        email = data.get('email')
        
        # SECURITY ISSUE: No rate limiting
        # SECURITY ISSUE: No CAPTCHA
        
        # SECURITY ISSUE: User enumeration vulnerability
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Email not found'}), 404  # Reveals email doesn't exist
        
        # SECURITY ISSUE: Predictable token generation
        reset_token = secrets.token_urlsafe(16)  # SECURITY ISSUE: Too short
        
        # SECURITY ISSUE: Token stored in plain text
        user.reset_token = reset_token
        
        # SECURITY ISSUE: Long token expiration
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        
        db.session.commit()
        
        # SECURITY ISSUE: Sending token in URL (can be logged)
        reset_link = f"http://localhost:5000/reset-password?token={reset_token}"
        
        # Send email (simulated)
        send_password_reset_email(user.email, reset_link)
        
        return jsonify({
            'message': 'Password reset link sent',
            'reset_token': reset_token  # SECURITY ISSUE: Exposing token in response
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        # SECURITY ISSUE: No input validation
        
        # SECURITY ISSUE: Token not hashed before lookup
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid token'}), 400
        
        # SECURITY ISSUE: No check if token is already used
        
        # Check token expiry
        if user.reset_token_expiry < datetime.utcnow():
            return jsonify({'error': 'Token expired'}), 400
        
        # SECURITY ISSUE: No password strength validation
        user.set_password(new_password)
        
        # SECURITY ISSUE: Token not invalidated properly - can be reused
        user.reset_token = None
        user.reset_token_expiry = None
        
        db.session.commit()
        
        # SECURITY ISSUE: No notification sent to user about password change
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password/validate-token', methods=['POST'])
def validate_reset_token():
    try:
        data = request.get_json()
        token = data.get('token')
        
        # SECURITY ISSUE: Token exposed in request
        
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 400
        
        if user.reset_token_expiry < datetime.utcnow():
            return jsonify({'valid': False, 'error': 'Token expired'}), 400
        
        # SECURITY ISSUE: Returning user information with token validation
        return jsonify({
            'valid': True,
            'user': user.to_dict()  # SECURITY ISSUE: Exposing user data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_password_reset_email(email, reset_link):
    # SECURITY ISSUE: Hardcoded SMTP credentials
    try:
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = 'paysecure@example.com'
        smtp_password = 'EmailPassword123!'  # SECURITY ISSUE: Hardcoded password
        
        msg = MIMEText(f'''
        Click the following link to reset your password:
        
        {reset_link}
        
        This link will expire in 24 hours.
        ''')
        
        msg['Subject'] = 'Password Reset Request'
        msg['From'] = smtp_user
        msg['To'] = email
        
        # SECURITY ISSUE: No error handling for email failures
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f'Password reset email sent to {email}')
        
    except Exception as e:
        # SECURITY ISSUE: Email failures not reported
        print(f'Failed to send email: {e}')
