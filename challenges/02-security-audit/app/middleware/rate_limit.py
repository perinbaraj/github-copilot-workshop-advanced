from flask import request, jsonify
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
import time

# SECURITY ISSUE: In-memory rate limiting (not scalable, not persistent)
rate_limit_storage = defaultdict(list)

class RateLimiter:
    """
    Simple rate limiter
    
    SECURITY ISSUES:
    - In-memory storage (lost on restart)
    - Not distributed (doesn't work with multiple servers)
    - Can be bypassed by changing IP
    - No sliding window
    """
    
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests  # SECURITY ISSUE: Too permissive default
        self.window = window  # Window in seconds
    
    def is_rate_limited(self, identifier):
        """
        Check if identifier is rate limited
        
        SECURITY ISSUE: Weak rate limit logic
        """
        current_time = time.time()
        
        # Clean old entries (PERFORMANCE ISSUE: O(n) operation)
        rate_limit_storage[identifier] = [
            timestamp for timestamp in rate_limit_storage[identifier]
            if current_time - timestamp < self.window
        ]
        
        # Check if rate limited
        if len(rate_limit_storage[identifier]) >= self.max_requests:
            return True
        
        # Add current request
        rate_limit_storage[identifier].append(current_time)
        return False
    
    def get_identifier(self):
        """
        Get identifier for rate limiting
        
        SECURITY ISSUE: Can be spoofed via X-Forwarded-For header
        """
        # SECURITY ISSUE: Trusting X-Forwarded-For without validation
        return request.headers.get('X-Forwarded-For', request.remote_addr)

def rate_limit(max_requests=100, window=60, per='ip'):
    """
    Rate limiting decorator
    
    SECURITY ISSUES:
    - Bypassable with IP spoofing
    - No progressive rate limiting
    - No differentiation between authenticated/anonymous
    """
    limiter = RateLimiter(max_requests, window)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # SECURITY ISSUE: Rate limit can be disabled by not setting identifier
            if per == 'ip':
                identifier = limiter.get_identifier()
            elif per == 'user':
                # SECURITY ISSUE: Not checking if user is authenticated
                identifier = getattr(request, 'current_user', None)
                if identifier:
                    identifier = f'user_{identifier.id}'
                else:
                    identifier = limiter.get_identifier()
            else:
                identifier = limiter.get_identifier()
            
            # SECURITY ISSUE: Rate limiter not enforced in all cases
            if limiter.is_rate_limited(identifier):
                # SECURITY ISSUE: Revealing rate limit information
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'max_requests': max_requests,
                    'window': window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def strict_rate_limit(max_requests=10, window=60):
    """
    Stricter rate limit for sensitive endpoints
    
    SECURITY ISSUE: Still bypassable
    """
    return rate_limit(max_requests=max_requests, window=window)

def check_rate_limit_status(identifier):
    """
    Check current rate limit status
    
    SECURITY ISSUE: Exposing rate limit information
    """
    current_time = time.time()
    
    requests = [
        timestamp for timestamp in rate_limit_storage[identifier]
        if current_time - timestamp < 60
    ]
    
    # SECURITY ISSUE: Revealing exact request count
    return {
        'requests_made': len(requests),
        'requests_remaining': 100 - len(requests),
        'reset_time': current_time + 60
    }

def reset_rate_limit(identifier):
    """
    Reset rate limit for identifier
    
    SECURITY ISSUE: No authorization check - anyone can reset
    """
    # SECURITY ISSUE: No authorization required to reset rate limits
    rate_limit_storage[identifier] = []
    return True

class IPBasedRateLimiter:
    """
    IP-based rate limiter
    
    SECURITY ISSUES:
    - Easily bypassed with VPN/proxy
    - No CAPTCHA integration
    - No progressive delays
    """
    
    def __init__(self):
        self.limits = {
            'login': (5, 300),  # 5 attempts per 5 minutes
            'api': (100, 60),   # 100 requests per minute
            'payment': (10, 60) # 10 payments per minute
        }
    
    def check(self, endpoint_type):
        """
        Check rate limit for endpoint type
        
        SECURITY ISSUE: Same implementation issues
        """
        max_requests, window = self.limits.get(endpoint_type, (100, 60))
        limiter = RateLimiter(max_requests, window)
        identifier = limiter.get_identifier()
        
        return not limiter.is_rate_limited(identifier)

# Global rate limiter instance
# SECURITY ISSUE: Global state, not thread-safe
global_rate_limiter = IPBasedRateLimiter()
