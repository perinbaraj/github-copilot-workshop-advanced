# PaySecure Security Vulnerabilities

## 🔴 Critical Vulnerabilities

### VULN-001: MD5 Password Hashing (CRITICAL)
**Location:** `app/server.py:45`  
**OWASP:** A02:2021 – Cryptographic Failures  
**Severity:** 🔴 Critical  
**CWE:** CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)

**Vulnerable Code:**
```python
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**Issue:**
- MD5 is a broken hash function
- No salt - identical passwords have identical hashes
- Fast computation allows brute-force attacks
- Rainbow tables exist for MD5

**Impact:**
- Attacker can crack all passwords in minutes
- User credentials completely compromised
- Compliance violations (PCI-DSS, GDPR)

**Proof of Concept:**
```python
import hashlib
# Common password
password = "password123"
md5_hash = hashlib.md5(password.encode()).hexdigest()
print(md5_hash)  # 482c811da5d5b4bc6d497ffa98491e38

# Attacker can reverse this with rainbow tables instantly
# hashcat -m 0 -a 0 hashes.txt rockyou.txt
```

**Fix:**
```python
import bcrypt

# Hashing (during registration)
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# Verification (during login)
if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
    # Password correct
```

**Expected Result:** Password cracking time: milliseconds → years

---

### VULN-002: SQL Injection (CRITICAL)
**Location:** `app/server.py:55, 102, 156`  
**OWASP:** A03:2021 – Injection  
**Severity:** 🔴 Critical  
**CWE:** CWE-89 (SQL Injection)

**Vulnerable Code:**
```python
cursor.execute(f"SELECT * FROM users WHERE email = '{email}' AND password_hash = '{password_hash}'")
```

**Issue:**
- Direct string interpolation in SQL queries
- No input sanitization
- Allows arbitrary SQL execution

**Proof of Concept:**
```bash
# Login bypass
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "anything' OR '1'='1"}'

# This creates the query:
# SELECT * FROM users WHERE email = 'admin@example.com' AND password_hash = 'anything' OR '1'='1'
# The OR '1'='1' always evaluates to true!

# Data extraction
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com' UNION SELECT * FROM credit_cards--", "password": "x"}'
```

**Impact:**
- Complete database compromise
- Data exfiltration (all user data, credit cards)
- Data modification/deletion
- Authentication bypass

**Fix:**
```python
# Use parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND password_hash = %s",
    (email, password_hash)
)
```

**Expected Result:** SQL injection attempts safely escaped

---

### VULN-003: Plain-Text Credit Card Storage (CRITICAL)
**Location:** `app/server.py:109`  
**OWASP:** A02:2021 – Cryptographic Failures  
**Severity:** 🔴 Critical  
**CWE:** CWE-311 (Missing Encryption of Sensitive Data)

**Vulnerable Code:**
```python
cursor.execute(f"""
    INSERT INTO payments (user_id, amount, credit_card, cvv, status)
    VALUES ({user_id}, {amount}, '{credit_card}', '{cvv}', 'completed')
""")
```

**Issue:**
- Credit card numbers stored in plain text
- CVV stored (PCI-DSS strictly forbids this)
- No encryption at rest
- Database breach = full card compromise

**Compliance Violations:**
- **PCI-DSS Requirement 3.2:** Cardholder data must not be stored after authorization
- **PCI-DSS Requirement 3.4:** PAN must be rendered unreadable
- **PCI-DSS Requirement 3.2.1:** Never store CVV

**Proof of Concept:**
```sql
-- Attacker with database access sees:
SELECT * FROM payments;
-- id | user_id | amount | credit_card        | cvv | status
-- 1  | 1       | 100.00 | 4532015112830366   | 123 | completed

-- Full card details exposed!
```

**Impact:**
- Massive fines (up to $500,000 per violation)
- Complete loss of PCI compliance
- Card fraud liability
- Reputational damage
- Potential criminal charges

**Fix:**
```python
# Use payment processor tokens (Stripe, PayPal)
import stripe
stripe.api_key = "sk_test_..."

# Create payment intent (card never touches your server)
intent = stripe.PaymentIntent.create(
    amount=amount * 100,  # cents
    currency='usd',
    customer=customer_id,
    payment_method=payment_method_id,
)

# Store only the token
cursor.execute(
    "INSERT INTO payments (user_id, amount, stripe_payment_id, status) VALUES (%s, %s, %s, %s)",
    (user_id, amount, intent['id'], 'pending')
)

# NEVER store CVV under any circumstances
```

**Expected Result:** Card data never stored, only secure tokens

---

### VULN-004: No Webhook Signature Verification (HIGH)
**Location:** `app/server.py:119-133`  
**OWASP:** A07:2021 – Identification and Authentication Failures  
**Severity:** 🟠 High  
**CWE:** CWE-345 (Insufficient Verification of Data Authenticity)

**Vulnerable Code:**
```python
@app.route('/api/webhooks/payment', methods=['POST'])
def payment_webhook():
    payload = request.get_json()
    # NO SIGNATURE VERIFICATION!
    payment_id = payload['payment_id']
    status = payload['status']
    # Update payment status directly
```

**Issue:**
- Anyone can send fake webhook requests
- No verification that webhook is from payment provider
- Attacker can mark payments as "completed" without paying

**Proof of Concept:**
```bash
# Attacker creates payment (gets ID 123)
# Payment is pending...

# Attacker sends fake webhook to complete it
curl -X POST http://localhost:5000/api/webhooks/payment \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": 123,
    "status": "completed",
    "amount": 0.01
  }'

# Payment marked as completed without actual payment!
# Attacker gets access to premium features for free
```

**Impact:**
- Payment fraud (free transactions)
- Revenue loss
- Accounting discrepancies
- Compliance issues

**Fix:**
```python
import hmac
import hashlib

@app.route('/api/webhooks/payment', methods=['POST'])
def payment_webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Stripe-Signature')
    
    # Verify signature
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Process verified webhook
    if event['type'] == 'payment_intent.succeeded':
        payment_id = event['data']['object']['id']
        # Update status
    
    return jsonify({'status': 'success'})
```

**Expected Result:** Only legitimate webhooks processed

---

### VULN-005: Exposed Admin Endpoints (HIGH)
**Location:** `app/server.py:136-154`  
**OWASP:** A01:2021 – Broken Access Control  
**Severity:** 🟠 High  
**CWE:** CWE-284 (Improper Access Control)

**Vulnerable Code:**
```python
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # NO AUTHENTICATION CHECK!
    cursor.execute("SELECT * FROM users")
    return jsonify(cursor.fetchall())
```

**Issue:**
- Admin endpoints have no authentication
- No authorization checks
- Anyone can access sensitive admin functions

**Proof of Concept:**
```bash
# Anonymous user can access all user data
curl http://localhost:5000/api/admin/users

# Anonymous user can access all transactions
curl http://localhost:5000/api/admin/transactions

# Response:
[
  {"id": 1, "email": "john@example.com", "password_hash": "...", "balance": 5000},
  {"id": 2, "email": "jane@example.com", "password_hash": "...", "balance": 10000}
]
```

**Impact:**
- Unauthorized access to all user data
- Privacy violations
- GDPR/data protection violations
- Reputational damage

**Fix:**
```python
from functools import wraps
import jwt

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Extract token (Bearer <token>)
            token = token.split(' ')[1] if ' ' in token else token
            
            # Verify token
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            
            # Check if user is admin
            if not payload.get('is_admin'):
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    cursor.execute("SELECT id, email, created_at FROM users")
    return jsonify(cursor.fetchall())
```

**Expected Result:** Admin endpoints require authentication + authorization

---

### VULN-006: Timing Attack in Authentication (MEDIUM)
**Location:** `app/server.py:51-68`  
**OWASP:** A07:2021 – Identification and Authentication Failures  
**Severity:** 🟡 Medium  
**CWE:** CWE-208 (Observable Timing Discrepancy)

**Vulnerable Code:**
```python
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
user = cursor.fetchone()

if not user:
    return jsonify({'error': 'Invalid credentials'}), 401  # Fast path

if user[2] != password_hash:
    return jsonify({'error': 'Invalid credentials'}), 401  # Slower path
```

**Issue:**
- Different execution time for valid vs invalid email
- Attacker can enumerate valid emails

**Proof of Concept:**
```python
import time
import requests

def test_email(email):
    start = time.time()
    response = requests.post('http://localhost:5000/api/login', json={
        'email': email,
        'password': 'wrongpassword'
    })
    return time.time() - start

# Invalid email: 0.05s (fast - user lookup fails immediately)
# Valid email: 0.15s (slow - password hash comparison)

# Attacker can determine valid emails
for email in potential_emails:
    if test_email(email) > 0.1:
        print(f"Valid email found: {email}")
```

**Impact:**
- Email enumeration
- Targeted phishing attacks
- Credential stuffing preparation

**Fix:**
```python
import time

cursor.execute(
    "SELECT id, email, password_hash, is_admin FROM users WHERE email = %s",
    (email,)
)
user = cursor.fetchone()

# Calculate password hash even if user doesn't exist
if user:
    stored_hash = user[2].encode('utf-8')
else:
    # Use dummy hash to prevent timing attacks
    stored_hash = bcrypt.hashpw(b'dummy', bcrypt.gensalt())

# Always perform hash comparison (constant time)
password_hash = bcrypt.hashpw(password.encode('utf-8'), stored_hash)

# Add small random delay
time.sleep(0.01 + random.random() * 0.02)

if not user or not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
    return jsonify({'error': 'Invalid credentials'}), 401

# Success
return jsonify({'token': generate_token(user)})
```

**Expected Result:** Constant-time authentication response

---

## 🟡 Medium Severity Vulnerabilities

### VULN-007: Weak JWT Secret
**Location:** `app/server.py:32`  
```python
JWT_SECRET = 'my-secret-key'  # Easily guessed
```

**Fix:**
```python
JWT_SECRET = os.environ.get('JWT_SECRET')  # Use environment variable
# Generate with: openssl rand -hex 32
```

---

### VULN-008: No Rate Limiting
**Location:** All authentication endpoints

**Impact:** Brute force attacks, DoS

**Fix:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ...
```

---

### VULN-009: No Input Validation
**Location:** All endpoints

**Fix:**
```python
from marshmallow import Schema, fields, validate, ValidationError

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

schema = LoginSchema()
try:
    data = schema.load(request.get_json())
except ValidationError as err:
    return jsonify(err.messages), 400
```

---

### VULN-010: Missing CSRF Protection
**Fix:**
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

---

## 📊 Vulnerability Summary

| ID | Severity | OWASP | Issue | Impact |
|----|----------|-------|-------|--------|
| VULN-001 | 🔴 Critical | A02 | MD5 password hashing | Complete credential compromise |
| VULN-002 | 🔴 Critical | A03 | SQL Injection | Full database access |
| VULN-003 | 🔴 Critical | A02 | Plain-text credit cards | PCI-DSS violation, fraud |
| VULN-004 | 🟠 High | A07 | No webhook verification | Payment fraud |
| VULN-005 | 🟠 High | A01 | Exposed admin endpoints | Unauthorized access |
| VULN-006 | 🟡 Medium | A07 | Timing attack | Email enumeration |
| VULN-007 | 🟡 Medium | A02 | Weak JWT secret | Token forgery |
| VULN-008 | 🟡 Medium | A04 | No rate limiting | Brute force attacks |
| VULN-009 | 🟡 Medium | A03 | No input validation | Injection attacks |
| VULN-010 | 🟡 Medium | A01 | No CSRF protection | Cross-site attacks |

---

## 🎯 Remediation Priority

### Phase 1: Critical (Immediate)
1. Replace MD5 with bcrypt
2. Fix all SQL injection with parameterized queries
3. Remove credit card storage, use payment tokens
4. Add webhook signature verification
5. Add authentication to admin endpoints

### Phase 2: High (24 hours)
1. Implement proper JWT secret management
2. Add rate limiting
3. Implement input validation
4. Add CSRF protection

### Phase 3: Enhancements (1 week)
1. Add security headers
2. Implement logging and monitoring
3. Add intrusion detection
4. Security audit and penetration testing
