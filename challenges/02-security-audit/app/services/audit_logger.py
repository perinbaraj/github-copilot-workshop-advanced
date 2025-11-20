import logging
from datetime import datetime
import json

# SECURITY ISSUE: Basic file logging, no centralized logging
# SECURITY ISSUE: Logs not encrypted
# SECURITY ISSUE: No log rotation
# SECURITY ISSUE: No log integrity checking

logger = logging.getLogger('audit')
logger.setLevel(logging.INFO)

# SECURITY ISSUE: Logs written to local file
handler = logging.FileHandler('audit.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AuditLogger:
    """
    Audit logging service
    
    SECURITY ISSUES:
    - Incomplete logging
    - No tamper protection
    - Sensitive data in logs
    - No real-time alerting
    """
    
    @staticmethod
    def log_login(user_id, username, ip_address, success=True):
        """
        Log login attempt
        
        SECURITY ISSUE: Not logging all relevant details
        """
        # SECURITY ISSUE: Logging username (could be sensitive)
        logger.info(f'Login attempt - User: {username}, IP: {ip_address}, Success: {success}')
    
    @staticmethod
    def log_transaction(user_id, transaction_type, amount, account_id):
        """
        Log transaction
        
        SECURITY ISSUE: Not logging enough context
        """
        # SECURITY ISSUE: Not logging recipient info
        # SECURITY ISSUE: Not logging transaction status
        logger.info(f'Transaction - User: {user_id}, Type: {transaction_type}, Amount: {amount}')
    
    @staticmethod
    def log_api_request(user_id, endpoint, method, ip_address):
        """
        Log API request
        
        SECURITY ISSUE: Not logging response or errors
        """
        logger.info(f'API Request - User: {user_id}, Endpoint: {endpoint}, Method: {method}, IP: {ip_address}')
    
    @staticmethod
    def log_security_event(event_type, user_id, details):
        """
        Log security event
        
        SECURITY ISSUE: No alerting mechanism
        """
        # SECURITY ISSUE: No escalation for critical events
        logger.warning(f'Security Event - Type: {event_type}, User: {user_id}, Details: {details}')
    
    @staticmethod
    def log_data_access(user_id, resource_type, resource_id, action):
        """
        Log data access
        
        SECURITY ISSUE: Not logging what data was accessed
        """
        logger.info(f'Data Access - User: {user_id}, Resource: {resource_type}:{resource_id}, Action: {action}')
    
    @staticmethod
    def log_permission_change(admin_id, target_user_id, old_role, new_role):
        """
        Log permission/role change
        
        SECURITY ISSUE: Not comprehensive enough
        """
        logger.warning(f'Permission Change - Admin: {admin_id}, Target: {target_user_id}, {old_role} -> {new_role}')
    
    @staticmethod
    def log_failed_authentication(username, ip_address, reason):
        """
        Log failed authentication
        
        SECURITY ISSUE: Not tracking failed attempt patterns
        """
        # SECURITY ISSUE: No lockout mechanism
        # SECURITY ISSUE: No brute force detection
        logger.warning(f'Failed Auth - Username: {username}, IP: {ip_address}, Reason: {reason}')
    
    @staticmethod
    def log_password_change(user_id, ip_address):
        """
        Log password change
        
        SECURITY ISSUE: Not logging who initiated change
        """
        logger.info(f'Password Change - User: {user_id}, IP: {ip_address}')
    
    @staticmethod
    def log_sensitive_data_access(user_id, data_type, record_id):
        """
        Log access to sensitive data
        
        SECURITY ISSUE: Not logging actual data fields accessed
        """
        # SECURITY ISSUE: Should log which fields were accessed
        logger.info(f'Sensitive Data Access - User: {user_id}, Type: {data_type}, Record: {record_id}')

def log_audit_event(event_type, user_id, data):
    """
    Generic audit logging function
    
    SECURITY ISSUE: Too generic, not structured
    """
    # SECURITY ISSUE: Logging raw data which might contain sensitive info
    logger.info(f'Audit Event - Type: {event_type}, User: {user_id}, Data: {json.dumps(data)}')

def get_audit_logs(user_id=None, start_date=None, end_date=None):
    """
    Retrieve audit logs
    
    SECURITY ISSUE: No access control on who can read logs
    SECURITY ISSUE: Reading from file directly (not scalable)
    """
    # SECURITY ISSUE: Anyone can call this function
    # SECURITY ISSUE: Returns all logs without filtering
    with open('audit.log', 'r') as f:
        logs = f.readlines()
    
    return logs

def clear_audit_logs():
    """
    Clear audit logs
    
    SECURITY ISSUE: No authorization check
    SECURITY ISSUE: No backup before clearing
    """
    # SECURITY ISSUE: Anyone can clear logs
    with open('audit.log', 'w') as f:
        f.write('')
    
    # SECURITY ISSUE: Not logging the fact that logs were cleared
    return True
