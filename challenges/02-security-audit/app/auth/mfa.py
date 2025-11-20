import pyotp
import qrcode
import io
import base64
from flask import request, jsonify, send_file
from app.auth import auth_bp
from app.models.user import User
from app import db

# SECURITY ISSUE: MFA implementation issues

@auth_bp.route('/mfa/setup', methods=['POST'])
def mfa_setup():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # SECURITY ISSUE: No authentication required to setup MFA
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # SECURITY ISSUE: MFA secret stored in plain text in database
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        db.session.commit()
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name='PaySecure'
        )
        
        # SECURITY ISSUE: Returning secret in response
        return jsonify({
            'secret': secret,  # SECURITY ISSUE: Exposing secret
            'qr_uri': totp_uri,
            'message': 'MFA setup initiated'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mfa/verify', methods=['POST'])
def mfa_verify():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        code = data.get('code')
        
        # SECURITY ISSUE: No rate limiting on MFA verification
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.mfa_secret:
            return jsonify({'error': 'MFA not set up'}), 400
        
        # SECURITY ISSUE: No brute force protection
        totp = pyotp.TOTP(user.mfa_secret)
        
        # SECURITY ISSUE: Allowing multiple verification attempts
        if totp.verify(code, valid_window=1):  # SECURITY ISSUE: Window too wide
            user.mfa_enabled = True
            db.session.commit()
            
            return jsonify({
                'message': 'MFA verified successfully',
                'mfa_enabled': True
            }), 200
        else:
            return jsonify({'error': 'Invalid MFA code'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mfa/disable', methods=['POST'])
def mfa_disable():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # SECURITY ISSUE: No password verification required to disable MFA
        # SECURITY ISSUE: No authentication check
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.mfa_enabled = False
        user.mfa_secret = None
        db.session.commit()
        
        return jsonify({'message': 'MFA disabled successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mfa/validate-login', methods=['POST'])
def mfa_validate_login():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        code = data.get('code')
        
        # SECURITY ISSUE: No rate limiting
        
        user = User.query.get(user_id)
        if not user or not user.mfa_enabled:
            return jsonify({'error': 'Invalid request'}), 400
        
        totp = pyotp.TOTP(user.mfa_secret)
        
        # SECURITY ISSUE: No lockout mechanism after failed attempts
        if totp.verify(code, valid_window=1):
            return jsonify({
                'message': 'MFA validation successful',
                'user': user.to_dict()  # SECURITY ISSUE: Exposing sensitive data
            }), 200
        else:
            return jsonify({'error': 'Invalid MFA code'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mfa/backup-codes', methods=['POST'])
def generate_backup_codes():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # SECURITY ISSUE: No authentication required
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # SECURITY ISSUE: Backup codes not implemented properly
        # SECURITY ISSUE: No secure storage of backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        return jsonify({
            'backup_codes': backup_codes,  # SECURITY ISSUE: Plain text backup codes
            'message': 'Backup codes generated'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
