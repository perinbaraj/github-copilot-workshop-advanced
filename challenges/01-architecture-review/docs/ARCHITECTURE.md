# TechMart E-Commerce Platform - Current Architecture

## System Overview

TechMart is a microservices-based e-commerce platform consisting of 6 services communicating through REST APIs and message queues.

## Services

### 1. API Gateway (Node.js/Express)
**Purpose**: Single entry point for all client requests

**Responsibilities**:
- Route requests to appropriate services
- Handle authentication
- Aggregate responses
- CORS handling

**Port**: 3000

**Current Issues**:
- ⚠️ No rate limiting
- ⚠️ Weak JWT secret
- ⚠️ No request timeouts
- ⚠️ Overly permissive CORS
- ⚠️ No circuit breaker pattern

### 2. User Service (Node.js/Express + PostgreSQL)
**Purpose**: User management and authentication

**Responsibilities**:
- User registration
- Authentication
- Profile management
- User data storage

**Port**: 3001
**Database**: PostgreSQL

**Current Issues**:
- ⚠️ Weak password hashing (4 salt rounds)
- ⚠️ No input validation
- ⚠️ N+1 query problems
- ⚠️ Missing database indexes
- ⚠️ No caching
- ⚠️ Mass assignment vulnerability

### 3. Product Catalog (Node.js/Express + MongoDB)
**Purpose**: Product information management

**Responsibilities**:
- Product CRUD operations
- Product search
- Inventory management
- Category management

**Port**: 3002
**Database**: MongoDB

**Current Issues**:
- ⚠️ No pagination
- ⚠️ Inefficient search queries
- ⚠️ Missing indexes
- ⚠️ No caching layer

### 4. Order Processing (Node.js/Express + PostgreSQL)
**Purpose**: Order management and fulfillment

**Responsibilities**:
- Order creation
- Order status tracking
- Inventory updates
- Order history

**Port**: 3003
**Database**: PostgreSQL

**Current Issues**:
- ⚠️ Missing foreign key constraints
- ⚠️ No transaction handling
- ⚠️ Synchronous processing (blocking)
- ⚠️ No retry logic

### 5. Payment Gateway (Python/Flask + PostgreSQL)
**Purpose**: Payment processing

**Responsibilities**:
- Payment authorization
- Payment capture
- Refund processing
- Payment history

**Port**: 5000
**Database**: PostgreSQL

**Current Issues**:
- ⚠️ Sensitive data in logs
- ⚠️ No PCI compliance
- ⚠️ Weak encryption
- ⚠️ No idempotency handling

### 6. Notification Service (Python)
**Purpose**: Send notifications to users

**Responsibilities**:
- Email notifications
- SMS notifications (planned)
- Push notifications (planned)

**Message Queue**: RabbitMQ

**Current Issues**:
- ⚠️ No retry logic
- ⚠️ No dead letter queue
- ⚠️ Synchronous email sending

## Infrastructure

### Databases
- **PostgreSQL**: User data, orders, payments
- **MongoDB**: Product catalog
- **Redis**: Session storage, caching (underutilized)

### Message Queue
- **RabbitMQ**: Async communication (underutilized)

## Data Flow

### Order Creation Flow
```
Client
  → API Gateway
  → Order Service (creates order)
  → Payment Service (processes payment)
  → Notification Service (sends email)
```

**Issues**:
- All synchronous, no async processing
- No saga pattern for distributed transactions
- No rollback mechanism on failure

## Known Performance Issues

1. **Database Performance**
   - Missing indexes on frequently queried columns
   - N+1 query problems in user service
   - No connection pooling optimization
   - Full table scans on product search

2. **API Performance**
   - No response caching
   - No request batching
   - Sequential API calls (should be parallel)
   - No pagination on list endpoints

3. **Scalability**
   - Services tightly coupled
   - No horizontal scaling strategy
   - Single database instances
   - No load balancing

## Known Security Issues

1. **Authentication/Authorization**
   - Weak JWT secret
   - No token expiration
   - No refresh tokens
   - Missing authorization checks
   - Timing attack vulnerabilities

2. **Data Protection**
   - Weak password hashing
   - Sensitive data in logs
   - No encryption at rest
   - SQL injection risks
   - Mass assignment vulnerabilities

3. **API Security**
   - No rate limiting
   - No input validation
   - Exposed internal errors
   - No HTTPS enforcement
   - Missing security headers

## Code Quality Issues

1. **Error Handling**
   - Inconsistent error responses
   - Stack traces exposed to clients
   - No centralized error handling
   - Missing error logging

2. **Code Organization**
   - No separation of concerns
   - Business logic in controllers
   - Duplicate code across services
   - No shared libraries

3. **Testing**
   - Minimal test coverage
   - No integration tests
   - No load tests
   - No security tests

## Architecture Issues

1. **Service Boundaries**
   - Unclear bounded contexts
   - Shared database tables
   - Tight coupling between services
   - God services (doing too much)

2. **Communication Patterns**
   - Over-reliance on synchronous calls
   - No event-driven architecture
   - No API versioning
   - Missing service discovery

3. **Resilience**
   - No circuit breakers
   - No retry logic
   - No fallback mechanisms
   - No graceful degradation

## Dependencies

### Node.js Services
- express: ^4.18.2
- pg: ^8.11.0
- mongodb: ^5.6.0
- redis: ^4.6.7
- axios: ^1.4.0
- bcrypt: ^5.1.0

### Python Services
- Flask: 2.3.2
- psycopg2: 2.9.6
- pika: 1.3.2
- requests: 2.31.0

## Deployment

Currently using Docker Compose for local development. No production deployment setup.

**Missing**:
- Kubernetes manifests
- CI/CD pipelines
- Monitoring and logging
- Auto-scaling configuration
- Backup strategies

## Metrics (Current State)

- **API Response Time**: 500ms - 2000ms (p95)
- **Database Query Time**: 100ms - 500ms
- **Orders/minute**: ~100 (max capacity unknown)
- **Uptime**: 95% (frequent crashes under load)
- **Test Coverage**: ~20%

## Priority Issues to Address

### Critical (P0)
1. Security vulnerabilities in authentication
2. Missing input validation
3. SQL injection risks
4. Weak password hashing
5. No rate limiting

### High (P1)
1. Database performance optimization
2. Missing indexes
3. N+1 query problems
4. No caching strategy
5. No error handling

### Medium (P2)
1. Code quality improvements
2. Testing coverage
3. API documentation
4. Monitoring setup
5. Service decoupling

## Team Structure

Currently a single team managing all services. Need to:
- Define service ownership
- Establish on-call rotation
- Create runbooks
- Set up knowledge base
