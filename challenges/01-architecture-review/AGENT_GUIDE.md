# Agent Guide for Multi-Agent Architecture Review

This guide provides effective prompts and strategies for using GitHub Copilot agents in the Architecture Review challenge.

## Creating Effective Agent Personas

### General Persona Template

```
You are a [ROLE] with [YEARS] years of experience specializing in:
- [Expertise Area 1]
- [Expertise Area 2]
- [Expertise Area 3]

[Specific task or analysis request]

Focus on [specific aspects].
Provide [expected output format].
```

## Agent Personas for This Challenge

### 1. Security Expert Agent

**Prompt**:
```
You are a senior application security engineer with 20 years of experience specializing in:
- OWASP Top 10 vulnerability identification and remediation
- API security and authentication best practices
- Secure coding practices for Node.js and Python
- SQL injection and XSS prevention
- Cryptography and data protection

Analyze the TechMart e-commerce platform for security vulnerabilities.
Review the API Gateway (services/api-gateway/src/server.js) and User Service (services/user-service/src/server.js).

For each vulnerability found, provide:
1. Vulnerability type (OWASP category)
2. Severity (Critical/High/Medium/Low)
3. File location and line number
4. Exploitation scenario
5. Remediation steps with code example
```

**Follow-up Prompts**:
```
Focus specifically on authentication vulnerabilities in the User Service.
What are the risks of using only 4 bcrypt salt rounds?
Show me how an attacker could exploit the mass assignment vulnerability.
Generate secure code to fix the weak JWT implementation.
```

### 2. Performance Engineer Agent

**Prompt**:
```
You are a performance engineering expert with extensive experience in:
- Node.js application performance optimization
- Database query optimization (PostgreSQL, MongoDB)
- Caching strategies with Redis
- API performance and latency reduction
- Load testing and capacity planning

Analyze the TechMart platform's performance characteristics.
Review services/user-service/src/server.js for performance bottlenecks.

Identify:
1. N+1 query problems
2. Missing database indexes
3. Caching opportunities
4. Synchronous operations that should be async
5. Resource-intensive operations

For each issue, estimate performance impact and improvement potential.
```

**Follow-up Prompts**:
```
What indexes should be added to the users table?
How can we optimize the getUserWithOrders function?
Design a caching strategy for user profile data.
What's the time complexity of the current user search?
```

### 3. Code Quality Engineer Agent

**Prompt**:
```
You are a code quality engineer specializing in:
- Clean Code principles and SOLID design
- Code smell detection and refactoring
- Error handling patterns
- Code organization and architecture
- Best practices for Node.js and Express

Review the API Gateway code for maintainability issues.
File: services/api-gateway/src/server.js

Identify:
1. Code duplication
2. Long functions that need decomposition
3. Missing error handling
4. Inconsistent patterns
5. Violation of separation of concerns
6. Missing input validation

Provide refactoring recommendations with code examples.
```

**Follow-up Prompts**:
```
How can we extract the authentication logic into middleware?
Suggest a better error handling pattern for this codebase.
What design patterns would improve this code?
Show me how to implement proper input validation.
```

### 4. API Architect Agent

**Prompt**:
```
You are an API architecture expert specializing in:
- RESTful API design best practices
- Microservices communication patterns
- API versioning strategies
- Service boundaries and contracts
- API security and rate limiting

Analyze the API design of the TechMart platform.
Review services/api-gateway/src/server.js and identify:

1. RESTful design violations
2. Missing API versioning
3. Inconsistent endpoint patterns
4. Missing rate limiting
5. CORS configuration issues
6. Missing request/response validation

Provide recommendations for API improvements.
```

**Follow-up Prompts**:
```
Design a proper API versioning strategy for this platform.
How should we implement rate limiting per endpoint?
What's the correct CORS configuration for a production API?
Show me how to add request validation middleware.
```

## Multi-Agent Workflow Strategies

### Parallel Analysis Pattern

Run multiple agents simultaneously on different aspects:

```
Agent 1 (Security): Review authentication in User Service
Agent 2 (Performance): Analyze database queries in User Service  
Agent 3 (Code Quality): Review error handling across services
Agent 4 (API Design): Evaluate API Gateway endpoint design
```

Then synthesize findings in a coordinator agent.

### Sequential Deep-Dive Pattern

Start broad, then go deep:

```
Step 1: Security Agent - High-level security scan of all services
Step 2: Security Agent - Deep dive into top 3 critical vulnerabilities
Step 3: Security Agent - Generate fix implementation for each
Step 4: Security Agent - Review fixes for completeness
```

### Cross-Referencing Pattern

Have agents review each other's findings:

```
Performance Agent: "The Security Agent found weak password hashing.
Does this impact performance? How many iterations should we use without
creating a performance bottleneck?"

Security Agent: "The Performance Agent suggests caching user data.
What security considerations should we address when caching sensitive data?"
```

## Effective Prompting Techniques

### 1. Be Specific About Scope

❌ Bad:
```
Review this code for issues.
```

✅ Good:
```
Review services/api-gateway/src/server.js lines 45-80 for:
- SQL injection vulnerabilities
- Missing input validation
- Authentication bypass risks

Provide specific line numbers and code examples for fixes.
```

### 2. Request Structured Output

```
Analyze the User Service authentication flow and provide:

## Vulnerabilities Found
For each vulnerability:
- **Type**: [vulnerability category]
- **Severity**: [Critical/High/Medium/Low]
- **Location**: [file:line]
- **Description**: [what's wrong]
- **Impact**: [potential damage]
- **Fix**: [code example]

## Security Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
```

### 3. Provide Context

```
Context: This is an e-commerce platform handling credit card payments.
It must comply with PCI-DSS requirements.

Current issue: Password hashing uses only 4 bcrypt rounds.

Questions:
1. What's the security risk?
2. What's the recommended number of rounds?
3. Will increasing rounds impact performance?
4. Show migration strategy for existing user passwords.
```

### 4. Iterate and Refine

```
Initial: "How can we improve API performance?"

Follow-up 1: "You mentioned adding Redis caching. Show me the implementation."

Follow-up 2: "What's the cache invalidation strategy for user profile updates?"

Follow-up 3: "How do we handle cache failures gracefully?"
```

## Common Agent Workflow Examples

### Example 1: Security Vulnerability Discovery and Fix

```
Step 1: Scan for vulnerabilities
"Analyze services/user-service/src/server.js for OWASP Top 10 vulnerabilities."

Step 2: Prioritize findings
"Of the vulnerabilities found, which 3 should be fixed first based on 
severity and exploitability?"

Step 3: Generate fixes
"For the SQL injection vulnerability at line 67, provide:
- Current vulnerable code
- Secure replacement code
- Test cases to verify the fix"

Step 4: Validate
"Review this fix code. Does it properly prevent SQL injection?
Are there any edge cases we missed?"
```

### Example 2: Performance Optimization

```
Step 1: Profile bottlenecks
"Analyze services/user-service/src/server.js for performance bottlenecks.
Focus on database queries and API response times."

Step 2: Quantify impact
"For the N+1 query problem in the getUsers endpoint, estimate:
- Current query count for 100 users
- Expected query count after optimization
- Performance improvement percentage"

Step 3: Implement optimization
"Show me how to rewrite the getUsers function to use eager loading
and reduce database queries from N+1 to 2 queries."

Step 4: Add monitoring
"Add performance instrumentation to measure query execution time
and track improvements after optimization."
```

## Tips for Agent Success

### DO:
- ✅ Start with specific, focused questions
- ✅ Provide file paths and line numbers
- ✅ Request code examples in responses
- ✅ Ask for trade-off analysis
- ✅ Iterate based on agent responses
- ✅ Validate agent suggestions
- ✅ Document agent insights

### DON'T:
- ❌ Ask vague, open-ended questions
- ❌ Analyze entire codebase at once
- ❌ Accept agent output without validation
- ❌ Skip providing context
- ❌ Forget to test agent-generated code
- ❌ Ignore security implications

## Agent Output Templates

### Vulnerability Report Template

```
# Security Vulnerability Report

## Executive Summary
[High-level findings]

## Critical Vulnerabilities (Immediate Action Required)

### 1. [Vulnerability Name]
- **Type**: [OWASP Category]
- **Severity**: Critical
- **Location**: `services/[service]/src/[file].js:line`
- **Description**: [What's wrong]
- **Exploitation**: [How to exploit]
- **Fix**: 
```javascript
// Current code
[vulnerable code]

// Fixed code
[secure code]
```
- **Testing**: [How to verify fix]

[Repeat for each vulnerability]
```

### Performance Analysis Template

```
# Performance Analysis Report

## Summary
[Overview of findings]

## Performance Bottlenecks

### 1. [Bottleneck Name]
- **Location**: `services/[service]/src/[file].js:line`
- **Impact**: [Current performance metrics]
- **Root Cause**: [Why it's slow]
- **Optimization**: [What to do]
- **Expected Improvement**: [Performance gain]
- **Implementation**:
```javascript
// Current code
[slow code]

// Optimized code
[fast code]
```

[Repeat for each bottleneck]
```

## Agent Coordination for Final Report

```
You are a technical program manager synthesizing findings from multiple expert agents.

Review these reports:
1. Security audit (15 vulnerabilities found)
2. Performance analysis (10 bottlenecks identified)
3. Code quality review (20 issues discovered)
4. API design review (8 improvements suggested)

Create a unified improvement plan:

1. **Critical Issues** (fix within 1 week)
2. **High Priority** (fix within 1 month)
3. **Medium Priority** (fix within quarter)
4. **Low Priority** (backlog)

For each issue:
- Impact on business
- Implementation effort
- Dependencies
- Risk if not fixed

Generate a phased implementation roadmap.
```

## Testing Agent Output

Always verify agent suggestions:

```
# Test security fixes
npm run test:security

# Test performance improvements
npm run test:performance

# Test functionality still works
npm run test:integration
```

## Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [PostgreSQL Performance](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)
