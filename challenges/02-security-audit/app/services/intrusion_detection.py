from datetime import datetime, timedelta
from collections import defaultdict
import re

# SECURITY ISSUE: In-memory storage, not persistent
suspicious_activities = defaultdict(list)
blocked_ips = set()
failed_login_attempts = defaultdict(int)

class IntrusionDetectionSystem:
    """
    Basic intrusion detection system
    
    SECURITY ISSUES:
    - Rule-based only, no ML
    - In-memory storage
    - No integration with firewall
    - No automated response
    """
    
    def __init__(self):
        # SECURITY ISSUE: Thresholds too high
        self.failed_login_threshold = 10  # Too permissive
        self.request_rate_threshold = 1000  # Too permissive
        self.suspicious_pattern_threshold = 5
        
        # SECURITY ISSUE: Patterns incomplete
        self.sql_injection_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bOR\b.*=.*)",
            r"(--)",
            r"(;.*DROP)",
        ]
        
        self.xss_patterns = [
            r"(<script.*?>)",
            r"(javascript:)",
            r"(onerror=)",
            r"(onload=)",
        ]
    
    def check_sql_injection(self, input_string):
        """
        Check for SQL injection patterns
        
        SECURITY ISSUE: Pattern matching is insufficient
        """
        if not isinstance(input_string, str):
            return False
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                # SECURITY ISSUE: Only logging, not blocking
                return True
        
        return False
    
    def check_xss_attack(self, input_string):
        """
        Check for XSS patterns
        
        SECURITY ISSUE: Incomplete XSS detection
        """
        if not isinstance(input_string, str):
            return False
        
        for pattern in self.xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return True
        
        return False
    
    def track_failed_login(self, username, ip_address):
        """
        Track failed login attempts
        
        SECURITY ISSUE: No IP blocking
        SECURITY ISSUE: No CAPTCHA integration
        """
        key = f"{username}:{ip_address}"
        failed_login_attempts[key] += 1
        
        # SECURITY ISSUE: Not actually blocking after threshold
        if failed_login_attempts[key] >= self.failed_login_threshold:
            # SECURITY ISSUE: Only tracking, not blocking
            suspicious_activities[ip_address].append({
                'type': 'brute_force',
                'username': username,
                'timestamp': datetime.now(),
                'count': failed_login_attempts[key]
            })
        
        return failed_login_attempts[key]
    
    def reset_failed_logins(self, username, ip_address):
        """
        Reset failed login counter
        
        SECURITY ISSUE: No authorization check
        """
        key = f"{username}:{ip_address}"
        # SECURITY ISSUE: Anyone can reset counters
        failed_login_attempts[key] = 0
    
    def check_suspicious_transaction(self, user_id, amount, frequency):
        """
        Check for suspicious transaction patterns
        
        SECURITY ISSUE: Basic heuristics only
        """
        # SECURITY ISSUE: Thresholds hardcoded and not user-specific
        if amount > 10000:
            return True, 'Large transaction amount'
        
        if frequency > 10:  # More than 10 transactions
            return True, 'High transaction frequency'
        
        # SECURITY ISSUE: No ML-based anomaly detection
        # SECURITY ISSUE: Not checking historical patterns
        
        return False, 'Normal transaction'
    
    def detect_account_takeover(self, user_id, current_ip, known_ips):
        """
        Detect potential account takeover
        
        SECURITY ISSUE: Simple IP check only
        """
        # SECURITY ISSUE: IP-based detection is unreliable
        # SECURITY ISSUE: No device fingerprinting
        # SECURITY ISSUE: No behavioral analysis
        
        if current_ip not in known_ips:
            return True, 'Login from unknown IP'
        
        return False, 'Normal login'
    
    def check_velocity_abuse(self, user_id, action_type, time_window=60):
        """
        Check for velocity abuse
        
        SECURITY ISSUE: Not implemented properly
        """
        # SECURITY ISSUE: Placeholder implementation
        return False
    
    def is_ip_blocked(self, ip_address):
        """
        Check if IP is blocked
        
        SECURITY ISSUE: No persistent storage
        """
        return ip_address in blocked_ips
    
    def block_ip(self, ip_address, reason):
        """
        Block an IP address
        
        SECURITY ISSUE: No authorization check
        SECURITY ISSUE: No expiration time
        """
        # SECURITY ISSUE: Anyone can block IPs
        blocked_ips.add(ip_address)
        
        suspicious_activities[ip_address].append({
            'type': 'blocked',
            'reason': reason,
            'timestamp': datetime.now()
        })
    
    def unblock_ip(self, ip_address):
        """
        Unblock an IP address
        
        SECURITY ISSUE: No authorization check
        """
        # SECURITY ISSUE: Anyone can unblock IPs
        if ip_address in blocked_ips:
            blocked_ips.remove(ip_address)
    
    def get_suspicious_activities(self, ip_address=None):
        """
        Get suspicious activities
        
        SECURITY ISSUE: No access control
        """
        # SECURITY ISSUE: Exposing all security data
        if ip_address:
            return suspicious_activities.get(ip_address, [])
        return dict(suspicious_activities)
    
    def analyze_user_behavior(self, user_id, actions):
        """
        Analyze user behavior for anomalies
        
        SECURITY ISSUE: Not implemented
        """
        # SECURITY ISSUE: Behavioral analysis not implemented
        return False, 'Analysis not implemented'

# Global IDS instance
# SECURITY ISSUE: Global state, not thread-safe
ids = IntrusionDetectionSystem()

def check_request_for_attacks(request_data):
    """
    Check request data for common attacks
    
    SECURITY ISSUE: Limited attack detection
    """
    issues = []
    
    if isinstance(request_data, dict):
        for key, value in request_data.items():
            if isinstance(value, str):
                if ids.check_sql_injection(value):
                    issues.append(f'Possible SQL injection in {key}')
                
                if ids.check_xss_attack(value):
                    issues.append(f'Possible XSS attack in {key}')
    
    # SECURITY ISSUE: Not blocking, only reporting
    return issues
