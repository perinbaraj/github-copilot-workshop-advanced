# Data Protection Guide - PaySecure

## Overview
This document outlines data protection standards and practices for the PaySecure financial application.

**⚠️ WORKSHOP NOTE: This application contains intentional data protection violations for training purposes.**

## Data Classification

### Payment Card Data (PCI-DSS Cardholder Data)
**Category:** Critical - PCI-DSS Protected

**Includes:**
- Primary Account Number (PAN) - Credit/debit card numbers
- Cardholder name
- Service code
- Expiration date

**Sensitive Authentication Data (SAD) - NEVER STORE:**
- ❌ CVV/CVC/CVV2/CVC2 (Card verification codes)
- ❌ Full magnetic stripe data
- ❌ PIN/PIN Block

**Current Violations in Application:**
```python
# CRITICAL PCI-DSS VIOLATIONS in app/models/payment.py:
- Full card_number stored in plaintext (16 digits)
- CVV stored in plaintext (NEVER ALLOWED)
- No encryption at rest
- Card data exposed in API responses (to_dict method)
```

**Required Protection:**
- ✅ Tokenization (replace PAN with token)
- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Truncation/masking in displays (show last 4 digits only)
- ✅ Secure deletion
- ❌ NEVER store CVV

### Personal Identifiable Information (PII)
**Category:** Sensitive

**Includes:**
- Social Security Numbers (SSN)
- Driver's license numbers
- Passport numbers
- Biometric data
- Date of birth
- Home address

**Current Issues:**
```python
# Vulnerabilities in app/models/user.py:
- SSN stored in plaintext
- Exposed in to_dict() API responses
- No encryption
- No data masking
```

**Required Protection:**
- Strong encryption (AES-256-GCM)
- Field-level encryption keys
- Redaction in logs
- Access controls
- Data masking in UI
- Secure deletion

### Financial Information
**Category:** Confidential

**Includes:**
- Account numbers
- Account balances
- Transaction history
- Credit scores
- Income information

**Current Issues:**
```python
# Vulnerabilities in app/models/account.py:
- Account numbers unencrypted
- IDOR vulnerabilities allow unauthorized access
- No data masking in responses
- Transaction details fully exposed
```

**Required Protection:**
- Encryption at rest
- Access control (ownership verification)
- Audit logging
- Data retention policies

### Authentication Data
**Category:** Critical

**Includes:**
- Passwords/password hashes
- Security questions/answers
- MFA secrets
- API keys
- Session tokens

**Current Issues:**
```python
# Vulnerabilities in app/auth/:
- MD5 password hashing (weak)
- MFA secrets exposed in API (mfa.py)
- Session tokens in memory only
- No token revocation
```

**Required Protection:**
- bcrypt/Argon2 for passwords (work factor 12+)
- Secure random generation
- Encrypted storage for MFA secrets
- Token blacklist mechanism
- Regular rotation

## Encryption Standards

### Encryption at Rest

#### Database Encryption
**Current State:** ❌ No encryption implemented

**Required:**
```python
# Should use SQLAlchemy encryption:
from sqlalchemy_utils import EncryptedType

class User(db.Model):
    ssn = Column(EncryptedType(String, encryption_key))
    # Separate keys per data classification
```

**Implementation:**
- Database-level encryption (TDE)
- Column-level encryption for sensitive fields
- Key management via KMS (AWS KMS, Azure Key Vault, HashiCorp Vault)
- Key rotation policy
- Separate encryption keys per data type

#### File Storage Encryption
- Encrypt files at rest
- Server-side encryption (SSE)
- Client-side encryption for highly sensitive data
- Encrypted backups

### Encryption in Transit

**Current Issues:**
```python
# app/payments/gateway.py:
verify_ssl=False  # SSL verification disabled!
```

**Required:**
- TLS 1.2 or higher only
- Strong cipher suites:
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
- Certificate validation enabled
- Certificate pinning for critical services
- HSTS header implementation

### Key Management

**Current Issues:**
```python
# app/config.py:
SECRET_KEY = 'dev-secret-key-change-in-production'  # Hardcoded!

# app/services/encryption.py:
ENCRYPTION_KEY = b'hardcoded_key_32_bytes_exactly!!'  # Hardcoded!
```

**Required Practices:**
- Store keys in secrets manager (AWS Secrets Manager, Azure Key Vault)
- Separate keys for different purposes
- Key rotation schedule:
  - Encryption keys: Annual
  - API keys: Quarterly
  - Session secrets: Monthly
- Key access auditing
- Hardware Security Module (HSM) for production

## Data Masking

### Display Masking

**Credit Cards:**
```python
# Current (VULNERABLE):
return {'card_number': '4532015112830366'}

# Required:
return {'card_number': '************0366'}  # Last 4 digits only
```

**SSN:**
```python
# Current (VULNERABLE):
return {'ssn': '123-45-6789'}

# Required:
return {'ssn': '***-**-6789'}  # Last 4 digits only
```

**Account Numbers:**
```python
# Current (VULNERABLE):
return {'account_number': '123456789'}

# Required:
return {'account_number': '*****6789'}  # Last 4 digits only
```

### Log Masking
**Current Issue:** Sensitive data appears in logs unredacted

**Required:**
```python
# app/services/audit_logger.py should mask:
def mask_sensitive_data(data):
    if 'card_number' in data:
        data['card_number'] = mask_card_number(data['card_number'])
    if 'ssn' in data:
        data['ssn'] = mask_ssn(data['ssn'])
    # ... other sensitive fields
    return data
```

## Data Retention

### Retention Periods

**Payment Card Data:**
- Authorization data: 90 days maximum
- Historical transactions: As required by business (with PAN masked)
- Audit logs: 1 year minimum

**PII:**
- Active users: Duration of account + 7 years
- Inactive users: Delete after 3 years of inactivity
- Marketing data: Until consent withdrawn + 30 days

**Financial Records:**
- Transaction records: 7 years (regulatory requirement)
- Account statements: 7 years
- Tax documents: 7 years

### Secure Deletion

**Current Issues:**
- No secure deletion process
- Soft deletes keep all data
- No data lifecycle management

**Required Process:**
```python
def secure_delete_user_data(user_id):
    # 1. Log deletion request
    audit_log('data_deletion', user_id)
    
    # 2. Delete PCI data immediately
    Payment.query.filter_by(user_id=user_id).delete()
    
    # 3. Anonymize transaction history
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    for trans in transactions:
        trans.user_id = None  # Anonymize
        trans.anonymized = True
    
    # 4. Delete PII after retention period
    # 5. Update audit trail
    # 6. Confirm deletion to user
```

## Data Minimization

### Principles
1. **Collect only what's necessary**
2. **Don't store what you don't need**
3. **Delete data when no longer required**

### Current Violations

**Unnecessary Data Collection:**
```python
# app/models/user.py:
# Storing fields that may not be necessary:
- Full SSN (last 4 digits usually sufficient)
- Date of birth (age range sufficient)
- Full address (zip code often enough)
```

**Better Approach:**
```python
class User(db.Model):
    ssn_last_four = Column(String(4))  # Instead of full SSN
    age_range = Column(String(10))  # Instead of DOB
    zip_code = Column(String(10))  # Instead of full address
```

## Access Controls

### Data Access Principles
1. **Least Privilege:** Users get minimum necessary access
2. **Need to Know:** Access only required data
3. **Separation of Duties:** No single person has complete control

### Current Issues

**IDOR Vulnerabilities:**
```python
# app/api/accounts.py:
@app.route('/api/accounts/<int:account_id>')
def get_account(account_id):
    account = Account.query.get(account_id)
    return jsonify(account.to_dict())
    
# MISSING: Ownership verification!
# Any authenticated user can access any account
```

**Required:**
```python
@app.route('/api/accounts/<int:account_id>')
@require_authentication
def get_account(account_id):
    account = Account.query.get_or_404(account_id)
    
    # Verify ownership
    if account.user_id != current_user.id and not is_admin():
        abort(403, 'Access denied')
    
    # Mask sensitive data for non-owners
    return jsonify(account.to_dict(mask_sensitive=True))
```

### Role-Based Access
**Data Access Matrix:**

| Role | PAN | CVV | SSN | Balance | Transactions |
|------|-----|-----|-----|---------|--------------|
| User | Masked | Never | Own Only | Own Only | Own Only |
| Support | Masked | Never | Last 4 | View Only | View Only |
| Admin | Last 4 | Never | Last 4 | All | All |
| Developer | No | Never | No | Test Data | Test Data |

## Data Breach Response

### Immediate Actions (< 1 hour)
1. Contain the breach
2. Assess scope of compromised data
3. Preserve evidence
4. Activate incident response team

### Data Types and Notification Requirements

**Payment Card Data Breach:**
- Notify payment processor: Immediately
- Notify card networks: Within 72 hours
- Notify customers: Within 72 hours
- PCI forensic investigation required

**PII Breach (GDPR):**
- Notify supervisory authority: Within 72 hours
- Notify affected users: Without undue delay
- Document the breach

**PII Breach (US State Laws):**
- California: Most expedient time, no later than required by statute
- Other states: Per applicable state law

### Customer Notification Template
```
Subject: Important Security Notice

Dear [Customer Name],

We are writing to inform you of a security incident that may have 
affected your personal information.

What Happened:
[Brief description of incident]

What Information Was Involved:
[List of data types: payment cards, SSN, etc.]

What We Are Doing:
[Steps taken to secure systems and prevent future incidents]

What You Can Do:
[Recommended actions: monitor accounts, credit monitoring offer, etc.]

For More Information:
[Contact information, dedicated hotline]
```

## Privacy Rights

### User Rights (GDPR/CCPA)

**Right to Access:**
- Users can request copy of their data
- Response time: 30 days
- Format: Machine-readable

**Right to Rectification:**
- Users can correct inaccurate data
- Update within 30 days

**Right to Erasure ("Right to be Forgotten"):**
- Delete personal data on request
- Exceptions: Legal requirements, legitimate interests
- Complete within 30 days

**Right to Data Portability:**
- Provide data in structured format
- Allow transfer to another service

### Implementation Status
**Current:** ❌ None of these rights implemented in application

**Required Endpoints:**
```python
# Should implement:
@app.route('/api/users/me/data', methods=['GET'])
def download_my_data():
    # Return all user data in JSON format
    
@app.route('/api/users/me/delete', methods=['POST'])
def delete_my_account():
    # Securely delete user data per retention policy
```

## Data Protection Impact Assessment (DPIA)

### When Required
- Processing of sensitive data (PII, payment data)
- Large-scale processing
- Systematic monitoring
- New technologies

### Assessment Process
1. Describe processing operations
2. Assess necessity and proportionality
3. Identify risks to individuals
4. Evaluate mitigation measures
5. Document findings

### Current Status
**This Application:** High-risk processing (payment data, PII)
**DPIA Status:** Required but not completed

## Compliance Monitoring

### Regular Audits
- **PCI-DSS:** Quarterly vulnerability scans, annual penetration test
- **Data access:** Monthly access review
- **Encryption:** Quarterly verification
- **Data retention:** Semi-annual cleanup

### Metrics to Track
- Data access patterns
- Failed access attempts
- Encryption coverage
- Data breach incidents
- Privacy rights requests
- Data retention compliance

## Training Requirements

### All Employees
- Annual data protection training
- Confidentiality agreements
- Incident reporting procedures

### Developers
- Secure coding practices
- Data protection by design
- Privacy-enhancing technologies
- Quarterly refresher training

### Access to Production Data
- Justified business need only
- Approval required
- Access logged and monitored
- Regular access reviews

## Technical Controls

### Database Security
**Current Issues:**
```sql
-- No encryption at rest
-- Default database credentials
-- No column-level access control
```

**Required:**
- Transparent Data Encryption (TDE)
- Column-level encryption for sensitive fields
- Database firewall
- Query monitoring and alerting
- Principle of least privilege

### Application Security
**Required:**
- Input validation and sanitization
- Output encoding (prevent XSS)
- Parameterized queries (prevent SQL injection)
- CSRF protection
- Security headers
- Rate limiting

### Network Security
- Network segmentation
- Database on private subnet
- Web application firewall (WAF)
- DDoS protection
- VPN for admin access

## Documentation Requirements

### Data Inventory
Maintain current inventory of:
- What data is collected
- Where data is stored
- Who has access
- How long retained
- How it's protected

### Processing Records
Document:
- Purpose of processing
- Categories of data
- Categories of recipients
- International transfers
- Security measures

---

**Last Updated:** 2024
**Version:** 1.0 (Training Exercise - Contains Intentional Vulnerabilities)
**Review Frequency:** Quarterly
