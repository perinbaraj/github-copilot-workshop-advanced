from flask import make_response

def add_security_headers(response):
    """
    Add security headers to response
    
    SECURITY ISSUES:
    - Missing critical headers
    - Weak Content Security Policy
    - Permissive CORS
    """
    
    # SECURITY ISSUE: No Content-Security-Policy header
    # SECURITY ISSUE: No X-Content-Type-Options header
    # SECURITY ISSUE: No X-Frame-Options header
    # SECURITY ISSUE: No Strict-Transport-Security header
    
    # SECURITY ISSUE: Weak CORS configuration
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    # SECURITY ISSUE: Exposing server information
    response.headers['X-Powered-By'] = 'Flask/2.3.2 Python/3.11'
    
    # SECURITY ISSUE: Allowing credentials with wildcard CORS
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

def init_security_headers(app):
    """
    Initialize security headers for Flask app
    
    SECURITY ISSUE: Not properly configured
    """
    
    @app.after_request
    def apply_security_headers(response):
        # SECURITY ISSUE: Very permissive CSP
        response.headers['Content-Security-Policy'] = "default-src *; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'"
        
        # SECURITY ISSUE: X-Frame-Options too permissive
        # Should be DENY or SAMEORIGIN
        # response.headers['X-Frame-Options'] = 'DENY'
        
        # SECURITY ISSUE: Not setting X-Content-Type-Options
        # response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # SECURITY ISSUE: Not setting Strict-Transport-Security
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # SECURITY ISSUE: Referrer policy too permissive
        response.headers['Referrer-Policy'] = 'unsafe-url'
        
        # SECURITY ISSUE: Permitting all features
        response.headers['Permissions-Policy'] = 'geolocation=*, microphone=*, camera=*'
        
        return response
    
    return app

class SecurityHeadersMiddleware:
    """
    Middleware class for security headers
    
    SECURITY ISSUE: Incomplete implementation
    """
    
    def __init__(self, app):
        self.app = app
        
        # SECURITY ISSUE: Using weak default headers
        self.headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'ALLOW-FROM *',  # SECURITY ISSUE: Too permissive
            'X-XSS-Protection': '0',  # SECURITY ISSUE: Disabled XSS protection
        }
    
    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # SECURITY ISSUE: Not actually applying headers properly
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

def set_secure_cookie_options(app):
    """
    Set secure cookie options
    
    SECURITY ISSUE: Insecure cookie configuration
    """
    
    # SECURITY ISSUE: Cookies not secure
    app.config['SESSION_COOKIE_SECURE'] = False
    
    # SECURITY ISSUE: Cookies not HttpOnly
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    
    # SECURITY ISSUE: SameSite not set
    app.config['SESSION_COOKIE_SAMESITE'] = None
    
    # SECURITY ISSUE: Long session lifetime
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 365  # 1 year
    
    return app
