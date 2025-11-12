#!/bin/bash

echo "Installing TechMart E-Commerce Platform..."
echo "==========================================="

# Install API Gateway
echo "Installing API Gateway..."
cd services/api-gateway
npm install
cd ../..

# Install User Service
echo "Installing User Service..."
cd services/user-service
npm install
cd ../..

# Install Product Catalog
echo "Installing Product Catalog..."
cd services/product-catalog
npm install
cd ../..

# Install Order Processing
echo "Installing Order Processing..."
cd services/order-processing
npm install
cd ../..

# Install Payment Gateway
echo "Installing Payment Gateway (Python)..."
cd services/payment-gateway
pip install -r requirements.txt
cd ../..

# Install Notification Service
echo "Installing Notification Service (Python)..."
cd services/notification-service
pip install -r requirements.txt
cd ../..

echo ""
echo "Installation complete!"
echo "To start all services, run: docker-compose up -d"
