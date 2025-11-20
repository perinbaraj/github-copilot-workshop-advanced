from flask import session, request, jsonify
from app.auth import auth_bp
from functools import wraps
from datetime import datetime, timedelta
import secrets

# SECURITY ISSUE: Session data stored in client-side cookies
# SECURITY ISSUE: No session timeout mechanism

class SessionManager:
    # SECURITY ISSUE: In-memory session store - not scalable
    active_sessions = {}
    
    @staticmethod
    def create_session(user_id, user_data):
        # SECURITY ISSUE: Predictable session ID
        session_id = secrets.token_hex(16)
        
        # SECURITY ISSUE: No session expiration
        SessionManager.active_sessions[session_id] = {
            'user_id': user_id,
            'user_data': user_data,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        return session_id
    
    @staticmethod
    def validate_session(session_id):
        # SECURITY ISSUE: No session hijacking protection
        if session_id not in SessionManager.active_sessions:
            return None
        
        session_data = SessionManager.active_sessions[session_id]
        
        # SECURITY ISSUE: No idle timeout check
        # SECURITY ISSUE: No absolute timeout check
        
        # Update last activity
        session_data['last_activity'] = datetime.utcnow()
        
        return session_data
    
    @staticmethod
    def destroy_session(session_id):
        if session_id in SessionManager.active_sessions:
            del SessionManager.active_sessions[session_id]
    
    @staticmethod
    def destroy_all_user_sessions(user_id):
        # SECURITY ISSUE: Inefficient session cleanup
        sessions_to_remove = []
        for session_id, session_data in SessionManager.active_sessions.items():
            if session_data['user_id'] == user_id:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del SessionManager.active_sessions[session_id]

def require_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # SECURITY ISSUE: Session token passed in header without proper validation
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 401
        
        session_data = SessionManager.validate_session(session_id)
        if not session_data:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # SECURITY ISSUE: No IP address validation for session hijacking protection
        # SECURITY ISSUE: No user agent validation
        
        request.session_data = session_data
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/session/create', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_data = data.get('user_data', {})
        
        # SECURITY ISSUE: No authentication before creating session
        
        session_id = SessionManager.create_session(user_id, user_data)
        
        return jsonify({
            'session_id': session_id,
            'message': 'Session created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/session/validate', methods=['POST'])
def validate_session():
    try:
        session_id = request.headers.get('X-Session-ID')
        
        session_data = SessionManager.validate_session(session_id)
        if not session_data:
            return jsonify({'valid': False}), 401
        
        # SECURITY ISSUE: Returning sensitive session data
        return jsonify({
            'valid': True,
            'session_data': session_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/session/destroy', methods=['POST'])
@require_session
def destroy_session():
    try:
        session_id = request.headers.get('X-Session-ID')
        SessionManager.destroy_session(session_id)
        
        return jsonify({'message': 'Session destroyed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/session/destroy-all', methods=['POST'])
def destroy_all_sessions():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # SECURITY ISSUE: No authentication required to destroy all sessions
        
        SessionManager.destroy_all_user_sessions(user_id)
        
        return jsonify({'message': 'All sessions destroyed'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
