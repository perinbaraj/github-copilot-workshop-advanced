# Write-Host "Installing TechMart E-Commerce Platform..." -ForegroundColor Green
Write-Host "==========================================="

# Install API Gateway
Write-Host "Installing API Gateway..." -ForegroundColor Cyan
Set-Location services/api-gateway
npm install
Set-Location ../..

# Install User Service
Write-Host "Installing User Service..." -ForegroundColor Cyan
Set-Location services/user-service
npm install
Set-Location ../..

# Install Product Catalog
Write-Host "Installing Product Catalog..." -ForegroundColor Cyan
Set-Location services/product-catalog
npm install
Set-Location ../..

# Install Order Processing
Write-Host "Installing Order Processing..." -ForegroundColor Cyan
Set-Location services/order-processing
npm install
Set-Location ../..

# Install Payment Gateway
Write-Host "Installing Payment Gateway (Python)..." -ForegroundColor Cyan
Set-Location services/payment-gateway
pip install -r requirements.txt
Set-Location ../..

# Install Notification Service
Write-Host "Installing Notification Service (Python)..." -ForegroundColor Cyan
Set-Location services/notification-service
pip install -r requirements.txt
Set-Location ../..

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "To start all services, run: docker-compose up -d"
