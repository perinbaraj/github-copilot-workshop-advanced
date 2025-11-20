# 🔒 Security Audit Agent Guide

## 🎯 Overview

This guide demonstrates how to use GitHub Copilot agents to conduct a comprehensive security audit of the PaySecure fintech application. You'll learn to leverage AI-powered security analysis to identify vulnerabilities, understand attack vectors, and implement remediation strategies.

---

## 🤖 Agent Capabilities for Security Audits

### 1. **Security Scanner Agent**
Identifies common vulnerabilities and security anti-patterns.

**Use Cases**:
- OWASP Top 10 detection
- Code pattern analysis
- Dependency vulnerability scanning
- Configuration review

### 2. **Threat Modeling Agent**
Analyzes attack surfaces and potential threats.

**Use Cases**:
- Attack vector identification
- Risk assessment
- Security boundary analysis
- Trust boundary mapping

### 3. **Compliance Agent**
Ensures adherence to security standards.

**Use Cases**:
- PCI-DSS compliance
- GDPR data protection
- SOC 2 controls
- Industry best practices

### 4. **Remediation Agent**
Provides secure code fixes and improvements.

**Use Cases**:
- Vulnerability patching
- Secure refactoring
- Security control implementation
- Testing security fixes

---

## 📝 Step-by-Step Security Audit Workflow

### Phase 1: Initial Security Assessment (15 minutes)

#### Step 1.1: Application Architecture Review

**Agent Prompt**:
```
Analyze the PaySecure application architecture in the workspace. 
Identify all:
1. Entry points (API endpoints, webhooks, authentication routes)
2. Data flows (user input → processing → storage)
3. External integrations (payment gateways, third-party services)
4. Trust boundaries (authentication/authorization checks)

Generate a security architecture diagram showing attack surfaces.
```

**Expected Output**:
- Architecture overview
- Entry point inventory
- Data flow diagram
- Trust boundary map

#### Step 1.2: Quick Vulnerability Scan

**Agent Prompt**:
```
Scan all Python files in app/ directory for common security vulnerabilities:
- SQL injection patterns
- Hardcoded secrets
- Weak cryptography
- Authentication bypasses
- Authorization issues
- XSS vulnerabilities
- Insecure deserialization
- Missing input validation

Provide a summary with severity ratings (Critical/High/Medium/Low).
```

**Expected Output**:
- Vulnerability count by severity
- File locations
- Affected endpoints
- Initial risk assessment

---

### Phase 2: OWASP Top 10 Analysis (30 minutes)

#### Step 2.1: A01 - Broken Access Control

**Agent Prompt**:
```
Review app/api/accounts.py and app/api/transactions.py for:
1. Insecure Direct Object Reference (IDOR) vulnerabilities
2. Missing authorization checks
3. Horizontal/vertical privilege escalation risks
4. Path traversal vulnerabilities

For each finding:
- Show the vulnerable code
- Explain the attack scenario
- Provide a secure code example
- Estimate the risk severity
```

**Files to Review**:
- `app/api/accounts.py` - IDOR vulnerability
- `app/api/transactions.py` - Missing ownership checks
- `app/permissions/rbac.py` - Authorization logic
- `app/permissions/ownership.py` - Resource ownership

#### Step 2.2: A02 - Cryptographic Failures

**Agent Prompt**:
```
Analyze cryptographic implementations in:
- app/auth/password.py (password hashing)
- app/services/encryption.py (data encryption)
- app/config.py (key management)
- app/models/payment.py (sensitive data storage)

Check for:
1. Weak hashing algorithms (MD5, SHA1)
2. Insufficient iteration counts
3. Missing salts
4. Hardcoded encryption keys
5. Insecure random number generation
6. PCI-DSS violations (storing CVV, full card numbers)

Provide recommendations for each issue.
```

**Critical Issues to Find**:
- MD5 password hashing
- Hardcoded encryption keys
- Storing full credit card numbers
- Storing CVV codes

#### Step 2.3: A03 - Injection

**Agent Prompt**:
```
Search for SQL injection vulnerabilities in:
- app/api/transactions.py
- app/api/accounts.py
- app/models/*.py

Look for:
1. Raw SQL queries with string concatenation
2. Unparameterized queries
3. Dynamic query construction
4. ORM query injection risks

For each vulnerability:
- Show the injection point
- Demonstrate an exploit payload
- Provide a parameterized query fix
```

**Test Payloads**:
```python
# SQL Injection test cases
query = "' OR '1'='1"
query = "'; DROP TABLE users; --"
query = "' UNION SELECT password FROM users --"
```

#### Step 2.4: A04 - Insecure Design

**Agent Prompt**:
```
Review the application design for security flaws:
1. Authentication mechanism (app/auth/)
2. Session management (app/auth/sessions.py)
3. Password reset flow (app/auth/reset_password.py)
4. MFA implementation (app/auth/mfa.py)
5. Rate limiting (app/middleware/rate_limit.py)

Identify design-level vulnerabilities:
- Missing security controls
- Weak authentication schemes
- Insecure session handling
- Account enumeration
- Timing attacks
```

#### Step 2.5: A05 - Security Misconfiguration

**Agent Prompt**:
```
Audit app/config.py and app/__init__.py for:
1. Debug mode in production
2. Exposed error messages
3. Default credentials
4. Missing security headers
5. Insecure CORS configuration
6. Overly permissive permissions
7. Unnecessary features enabled

List all misconfigurations with remediation steps.
```

**Configuration Files**:
- `app/__init__.py` - Flask app configuration
- `app/config.py` - Application settings
- `app/middleware/security_headers.py` - HTTP headers

#### Step 2.6: A06 - Vulnerable and Outdated Components

**Agent Prompt**:
```
Analyze requirements.txt for:
1. Packages with known CVEs
2. Outdated dependencies
3. Unnecessary packages
4. Unmaintained libraries

Use vulnerability databases to check each dependency.
Generate an upgrade plan prioritizing critical vulnerabilities.
```

#### Step 2.7: A07 - Identification and Authentication Failures

**Agent Prompt**:
```
Review authentication implementation in app/auth/:
1. Weak password policies (password.py)
2. Missing brute-force protection
3. Insecure session management (sessions.py)
4. Credential stuffing vulnerabilities
5. Missing MFA enforcement (mfa.py)
6. Password reset vulnerabilities (reset_password.py)

Test scenarios:
- Brute force login attempts
- Session fixation attacks
- Token theft and replay
- Password reset token prediction
```

#### Step 2.8: A08 - Software and Data Integrity Failures

**Agent Prompt**:
```
Check for integrity issues in:
1. Webhook signature validation (app/api/webhooks.py)
2. Update mechanisms
3. Deserialization (if pickle/yaml used)
4. CI/CD pipeline security

Verify:
- Digital signatures on webhooks
- Secure update channels
- Safe deserialization practices
```

#### Step 2.9: A09 - Security Logging and Monitoring Failures

**Agent Prompt**:
```
Review app/services/audit_logger.py for:
1. Missing security event logging
2. Insufficient log detail
3. Log injection vulnerabilities
4. Missing alerting on critical events
5. Log retention policies

Critical events to log:
- Failed authentication attempts
- Authorization failures
- Payment transactions
- Account changes
- Suspicious activities
```

#### Step 2.10: A10 - Server-Side Request Forgery (SSRF)

**Agent Prompt**:
```
Search for SSRF vulnerabilities:
1. User-controlled URLs
2. Webhook callback URLs
3. File upload processing
4. External API calls

Check app/payments/gateway.py and app/api/webhooks.py.
```

---

### Phase 3: PCI-DSS Compliance Review (20 minutes)

#### Step 3.1: Cardholder Data Storage

**Agent Prompt**:
```
Audit app/models/payment.py for PCI-DSS violations:
1. Storing full Primary Account Number (PAN)
2. Storing Card Verification Value (CVV/CVC)
3. Storing PIN data
4. Unencrypted cardholder data
5. Missing data retention policies

PCI-DSS Requirements:
- Requirement 3: Protect stored cardholder data
- Requirement 4: Encrypt transmission of cardholder data

Generate a compliance gap analysis.
```

**Critical Findings**:
- CVV storage (PCI-DSS violation)
- Full card number storage
- Unencrypted sensitive data

#### Step 3.2: Secure Transmission

**Agent Prompt**:
```
Review app/payments/gateway.py for:
1. SSL/TLS verification disabled
2. Weak cipher suites
3. Outdated TLS versions
4. Certificate validation bypassed
5. Insecure API calls to payment gateways

Verify all payment data is transmitted over secure channels.
```

#### Step 3.3: Access Control

**Agent Prompt**:
```
Check app/permissions/rbac.py for:
1. Role-based access to cardholder data
2. Principle of least privilege
3. Access logging and monitoring
4. Multi-factor authentication for admin access

Ensure compliance with PCI-DSS Requirement 7.
```

---

### Phase 4: Vulnerability Remediation (30 minutes)

#### Step 4.1: Critical Vulnerabilities (P0)

**Priority Order**:
1. SQL Injection (VULN-001)
2. Weak Password Hashing (VULN-002)
3. Hardcoded Secrets (VULN-006)
4. PCI-DSS Violations (VULN-005)

**Agent Prompt for SQL Injection Fix**:
```
Fix SQL injection in app/api/transactions.py:
1. Replace raw SQL with parameterized queries
2. Use SQLAlchemy ORM properly
3. Implement input validation
4. Add output encoding
5. Write unit tests to verify the fix

Show before/after code comparison.
```

**Agent Prompt for Password Hashing Fix**:
```
Upgrade password hashing in app/auth/password.py:
1. Replace MD5 with bcrypt/Argon2
2. Use secure salt generation
3. Implement sufficient work factor (cost=12 for bcrypt)
4. Add password strength requirements
5. Migrate existing passwords

Provide a migration script for existing users.
```

**Agent Prompt for Secrets Management**:
```
Remove hardcoded secrets from app/config.py:
1. Move secrets to environment variables
2. Use a secrets management service (AWS Secrets Manager, HashiCorp Vault)
3. Implement secret rotation
4. Add .env.example template
5. Update deployment documentation

Ensure no secrets in git history.
```

#### Step 4.2: High Severity Vulnerabilities (P1)

**Agent Prompt for IDOR Fix**:
```
Fix IDOR vulnerability in app/api/accounts.py:
1. Add ownership verification before operations
2. Implement resource-level authorization
3. Use app/permissions/ownership.py helper
4. Add authorization unit tests
5. Audit all similar endpoints

Ensure users can only access their own resources.
```

**Agent Prompt for XSS Prevention**:
```
Implement XSS protection:
1. Add output encoding in API responses
2. Set Content-Security-Policy headers
3. Validate and sanitize all user inputs
4. Use context-aware escaping
5. Add XSS unit tests

Review app/middleware/input_validation.py.
```

#### Step 4.3: Medium Severity Vulnerabilities (P2)

**Agent Prompt for Rate Limiting**:
```
Implement rate limiting in app/middleware/rate_limit.py:
1. Add Flask-Limiter dependency
2. Configure per-endpoint limits
3. Implement IP-based rate limiting
4. Add authenticated user rate limiting
5. Configure Redis for distributed rate limiting

Protect login, registration, and payment endpoints.
```

**Agent Prompt for Security Headers**:
```
Configure security headers in app/middleware/security_headers.py:
1. Strict-Transport-Security (HSTS)
2. X-Content-Type-Options: nosniff
3. X-Frame-Options: DENY
4. Content-Security-Policy
5. X-XSS-Protection
6. Referrer-Policy

Add middleware to all responses.
```

---

### Phase 5: Security Testing (15 minutes)

#### Step 5.1: Automated Security Tests

**Agent Prompt**:
```
Create comprehensive security tests in tests/security/:
1. test_auth.py - Authentication bypass tests
2. test_authorization.py - IDOR and access control tests
3. test_injection.py - SQL injection test cases
4. test_xss.py - Cross-site scripting tests
5. test_payment_security.py - PCI-DSS compliance tests

Each test should:
- Attempt to exploit the vulnerability
- Verify the fix prevents the attack
- Use realistic attack payloads
```

**Test Coverage Requirements**:
- Authentication: 90%+
- Authorization: 95%+
- Input validation: 85%+
- Payment processing: 100%

#### Step 5.2: Penetration Testing Scenarios

**Agent Prompt**:
```
Generate penetration testing scripts for:
1. Brute force attacks on /auth/login
2. SQL injection on /api/transactions
3. IDOR testing on /api/accounts/<id>
4. Session hijacking attempts
5. CSRF token bypass
6. Payment manipulation

Use tools: SQLMap, Burp Suite, OWASP ZAP configurations.
```

#### Step 5.3: Security Regression Tests

**Agent Prompt**:
```
Create regression test suite to prevent security vulnerabilities:
1. Pre-commit hooks for secret scanning
2. SAST integration (Bandit, Semgrep)
3. Dependency vulnerability scanning
4. Security header validation
5. Authentication flow testing

Add to CI/CD pipeline.
```

---

### Phase 6: Documentation and Reporting (10 minutes)

#### Step 6.1: Security Audit Report

**Agent Prompt**:
```
Generate a comprehensive security audit report:
1. Executive Summary
   - Total vulnerabilities found
   - Severity breakdown
   - Risk score
   - Remediation status

2. Detailed Findings
   - Each vulnerability with:
     * Description
     * Location (file/line)
     * Severity (CVSS score)
     * Attack scenario
     * Remediation steps
     * Proof of concept

3. Compliance Assessment
   - OWASP Top 10 status
   - PCI-DSS compliance gaps
   - Industry best practices

4. Remediation Roadmap
   - Priority matrix
   - Timeline
   - Resources needed

5. Risk Assessment
   - Business impact
   - Likelihood
   - Risk mitigation strategies

Format as professional security audit document.
```

#### Step 6.2: Developer Security Guidelines

**Agent Prompt**:
```
Create docs/SECURE_DEVELOPMENT.md with:
1. Secure coding standards
2. Common vulnerability patterns to avoid
3. Security review checklist
4. Testing requirements
5. Incident response procedures
6. Security resources and training

Make it actionable for developers.
```

#### Step 6.3: Compliance Documentation

**Agent Prompt**:
```
Update compliance documentation:
1. docs/DATA_PROTECTION.md - GDPR compliance
2. docs/ACCESS_CONTROL.md - Authorization policies
3. docs/SECURITY_POLICY.md - Overall security posture
4. docs/INCIDENT_RESPONSE.md - Security incident procedures

Ensure all policies are up to date.
```

---

## 🎯 Success Criteria

### Security Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Critical Vulnerabilities | 0 | 10+ | ❌ |
| High Severity Issues | < 3 | 15+ | ❌ |
| Medium Severity Issues | < 10 | 20+ | ❌ |
| Test Coverage | > 80% | ~40% | ❌ |
| PCI-DSS Compliance | 100% | 30% | ❌ |
| OWASP Top 10 Coverage | 10/10 | 0/10 | ❌ |

### Post-Remediation Targets

| Metric | Target | Status |
|--------|--------|--------|
| Critical Vulnerabilities | 0 | ✅ |
| High Severity Issues | 0 | ✅ |
| Medium Severity Issues | < 3 | ✅ |
| Test Coverage | 85% | ✅ |
| PCI-DSS Compliance | 100% | ✅ |
| OWASP Top 10 Coverage | 10/10 | ✅ |
| Security Headers | All Set | ✅ |
| Rate Limiting | Enabled | ✅ |
| Secrets Management | Externalized | ✅ |

---

## 🔍 Advanced Agent Techniques

### 1. Context-Aware Security Analysis

**Agent Prompt**:
```
Analyze the security context of app/api/transactions.py:
1. What sensitive data does it handle?
2. What are the trust boundaries?
3. What are the potential attack vectors?
4. What security controls are missing?
5. How would you exploit this endpoint?

Provide a detailed threat model.
```

### 2. Comparative Security Analysis

**Agent Prompt**:
```
Compare the current implementation in app/auth/password.py 
with industry best practices:
1. OWASP Password Storage Cheat Sheet
2. NIST Digital Identity Guidelines
3. CWE-916 (Weak Password Hashing)

Generate a gap analysis and remediation plan.
```

### 3. Security Code Review Automation

**Agent Prompt**:
```
Perform an automated security code review:
1. Scan all files for security anti-patterns
2. Check compliance with security checklist
3. Identify potential vulnerabilities
4. Suggest improvements
5. Prioritize by risk

Generate a pull request with fixes.
```

### 4. Threat Intelligence Integration

**Agent Prompt**:
```
Analyze the codebase against known attack patterns:
1. MITRE ATT&CK framework techniques
2. Recent CVE patterns in dependencies
3. Common fintech attack vectors
4. Zero-day vulnerability patterns

Provide proactive security recommendations.
```

---

## 🛠️ Tools and Resources

### Security Scanning Tools
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability checker
- **SQLMap** - SQL injection testing
- **OWASP ZAP** - Web application security scanner
- **Semgrep** - Static analysis

### Compliance Tools
- **PCI-DSS Scanner** - Payment card compliance
- **GDPR Checker** - Data protection compliance
- **SOC 2 Audit** - Security controls validation

### Testing Tools
- **Pytest** - Unit testing framework
- **Hypothesis** - Property-based testing
- **Faker** - Test data generation
- **VCR.py** - HTTP interaction recording

---

## 📚 Learning Resources

### OWASP Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### PCI-DSS Resources
- [PCI Security Standards](https://www.pcisecuritystandards.org/)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/document_library/)

### Secure Coding
- [CERT Secure Coding Standards](https://www.securecoding.cert.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 💡 Tips for Success

### 1. **Start with Quick Wins**
Focus on easily fixable issues first (hardcoded secrets, missing headers) to build momentum.

### 2. **Prioritize by Risk**
Use a risk-based approach: `Risk = Likelihood × Impact`. Fix critical issues first.

### 3. **Test Everything**
Write security tests for every vulnerability before and after fixing to prevent regression.

### 4. **Think Like an Attacker**
For each vulnerability, ask: "How would I exploit this? What's the worst-case scenario?"

### 5. **Document Everything**
Keep detailed records of findings, fixes, and testing for compliance and future reference.

### 6. **Use Agent Iterations**
Don't expect perfect results in one prompt. Refine and iterate with follow-up questions.

### 7. **Verify Fixes**
Always manually verify that agent-suggested fixes actually work and don't introduce new issues.

### 8. **Stay Updated**
Security is evolving. Keep agent prompts updated with latest threat intelligence.

---

## 🎓 Common Pitfalls

### ❌ Don't Do This
- **Fixing symptoms, not root causes** - Understand the underlying security flaw
- **Over-relying on automated tools** - Manual review is essential
- **Ignoring low/medium issues** - They can be chained into critical exploits
- **Skipping security tests** - Untested fixes may not work
- **Hard-coding fixes** - Use configurable security controls
- **Breaking functionality** - Security fixes should maintain application features

### ✅ Do This Instead
- **Understand the vulnerability class** - Learn the pattern, not just the instance
- **Combine automated and manual testing** - Best of both worlds
- **Fix all issues systematically** - Even "minor" vulnerabilities matter
- **Write comprehensive tests** - Prevent regression
- **Use security frameworks** - Leverage battle-tested solutions
- **Test thoroughly** - Ensure security and functionality

---

## 🚀 Next Steps

After completing this security audit:

1. **Implement findings** - Remediate all vulnerabilities
2. **Automate security** - Add security scanning to CI/CD
3. **Train team** - Share security knowledge
4. **Monitor continuously** - Set up security monitoring
5. **Regular audits** - Schedule periodic security reviews
6. **Stay informed** - Follow security advisories

---

**Good luck with your security audit! Remember: security is a journey, not a destination.** 🔒
