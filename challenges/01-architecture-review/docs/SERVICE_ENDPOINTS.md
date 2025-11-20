# TechMart Service Endpoints

This document provides a comprehensive overview of all service endpoints in the TechMart microservices architecture.

---

## API Gateway (Port 3000)

The API Gateway serves as the single entry point for all client requests and routes them to appropriate backend services.

### Authentication
- `POST /api/auth/login` - User login
  - Request: `{ "email": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": {...} }`

- `POST /api/auth/register` - User registration
  - Request: `{ "name": "string", "email": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": {...} }`

### Users
- `GET /api/users/:id` - Get user by ID
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ "id": number, "name": "string", "email": "string" }`

- `PUT /api/users/:id` - Update user
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ "name": "string", "email": "string" }`
  - Response: `{ "message": "User updated" }`

- `DELETE /api/admin/users/:id` - Delete user (admin only)
  - Headers: `Authorization: Bearer <token>`, `x-admin-key: <admin-secret>`
  - Response: `{ "message": "User deleted" }`

### Products
- `GET /api/products` - List all products
  - Response: `[{ "id": "string", "name": "string", "price": number, ... }]`

- `GET /api/products/:id` - Get product details
  - Response: `{ "id": "string", "name": "string", "description": "string", "price": number, ... }`

- `GET /api/products/search?query=<term>` - Search products
  - Query params: `query` (string)
  - Response: `[{ "id": "string", "name": "string", ... }]`

- `POST /api/products` - Create product
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ "name": "string", "description": "string", "price": number, "category": "string", "stock": number }`
  - Response: `{ "id": "string" }`

- `PUT /api/products/:id` - Update product
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ "name": "string", "price": number, ... }`
  - Response: `{ "message": "Product updated" }`

### Orders
- `POST /api/orders` - Create order
  - Headers: `Authorization: Bearer <token>`
  - Request: `{ "userId": number, "items": [{ "productId": "string", "quantity": number }] }`
  - Response: `{ "orderId": number, "totalAmount": number, "status": "string" }`

- `GET /api/orders/:id` - Get order details
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ "id": number, "userId": number, "totalAmount": number, "items": [...] }`

- `GET /api/users/:userId/orders` - Get user orders
  - Headers: `Authorization: Bearer <token>`
  - Response: `[{ "id": number, "totalAmount": number, "status": "string", ... }]`

---

## User Service (Port 3001)

Internal service for user management. Not directly accessible from outside the network.

- `POST /users/register` - Register new user
  - Request: `{ "name": "string", "email": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": {...} }`

- `POST /users/login` - Login user
  - Request: `{ "email": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": {...} }`

- `GET /users/:id` - Get user profile
  - Response: `{ "id": number, "name": "string", "email": "string", "role": "string" }`

- `PUT /users/:id` - Update user
  - Request: `{ "name": "string", "email": "string", "password": "string" }`
  - Response: `{ "message": "User updated successfully" }`

- `DELETE /users/:id` - Delete user
  - Response: `{ "message": "User deleted successfully" }`

---

## Product Catalog (Port 3002)

Internal service for product management using MongoDB.

- `GET /products` - List all products
  - Response: `[{ "_id": "string", "name": "string", "price": number, "stock": number, ... }]`

- `GET /products/:id` - Get product
  - Response: `{ "_id": "string", "name": "string", "description": "string", "price": number, ... }`

- `GET /products/search?query=<term>` - Search products
  - Query params: `query` (string)
  - Response: `[{ "_id": "string", "name": "string", ... }]`

- `POST /products` - Create product
  - Request: `{ "name": "string", "description": "string", "price": number, "category": "string", "stock": number }`
  - Response: `{ "id": "string" }`

- `PUT /products/:id` - Update product
  - Request: `{ "name": "string", "price": number, "stock": number, ... }`
  - Response: `{ "message": "Product updated" }`

---

## Order Processing (Port 3003)

Internal service for order management and processing.

- `POST /orders` - Create order
  - Request: `{ "userId": number, "items": [{ "productId": "string", "quantity": number }] }`
  - Response: `{ "orderId": number, "totalAmount": number, "status": "string" }`

- `GET /orders/:id` - Get order
  - Response: `{ "id": number, "user_id": number, "total_amount": number, "status": "string", "items": [...] }`

- `GET /users/:userId/orders` - User's orders
  - Response: `[{ "id": number, "total_amount": number, "status": "string", "created_at": "string" }]`

---

## Payment Gateway (Port 5000)

Internal Python Flask service for payment processing.

- `POST /payments/process` - Process payment
  - Request: `{ "orderId": number, "amount": number, "userId": number }`
  - Response: `{ "paymentId": number, "transactionId": "string", "status": "string" }`

- `GET /payments/<payment_id>` - Get payment details
  - Response: `{ "id": number, "orderId": number, "userId": number, "amount": number, "transactionId": "string", "status": "string" }`

- `POST /payments/webhook` - Payment webhook
  - Request: `{ "event": "string", "data": {...} }`
  - Response: `{ "status": "received" }`

---

## Notification Service

Background service that consumes messages from RabbitMQ. No HTTP endpoints - communicates via message queue only.

**Message Queue**: `orders`
- Consumes order events and sends email notifications
- Message format: `{ "orderId": number, "userId": number, "totalAmount": number }`

---

## Infrastructure Services

### PostgreSQL (Port 5432)
- Database: `techmart`
- User: `admin`
- Stores: users, orders, order_items, payments

### MongoDB (Port 27017)
- Database: `products`
- Stores: product catalog

### Redis (Port 6379)
- Used for caching (configured but not fully implemented)

### RabbitMQ (Ports 5672, 15672)
- Message broker for async communication
- Management UI: http://localhost:15672
- Queue: `orders`

---

## Notes

**Security Issues:**
- Many endpoints lack proper authentication/authorization
- Input validation is minimal or missing
- Some endpoints expose sensitive data

**Performance Issues:**
- No pagination on list endpoints
- Missing caching layer
- N+1 query problems in several services

These issues are intentional for the workshop challenge.
