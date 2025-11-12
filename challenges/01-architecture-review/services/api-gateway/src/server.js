const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const axios = require('axios');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3000;

// SECURITY ISSUE: Weak JWT secret
const JWT_SECRET = 'secret';

// SECURITY ISSUE: Overly permissive CORS
app.use(cors({
  origin: '*',
  credentials: true
}));

app.use(express.json({ limit: '50mb' })); // SECURITY ISSUE: No limit on request size
app.use(morgan('combined'));

// PERFORMANCE ISSUE: No rate limiting
// SECURITY ISSUE: No authentication middleware

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// SECURITY ISSUE: Authentication endpoint with weak validation
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // SECURITY ISSUE: No input validation
    // PERFORMANCE ISSUE: Synchronous call, no timeout
    const response = await axios.post(`${process.env.USER_SERVICE_URL}/users/authenticate`, {
      email,
      password
    });

    if (response.data.user) {
      // SECURITY ISSUE: Token with no expiration
      const token = jwt.sign({ userId: response.data.user.id }, JWT_SECRET);
      res.json({ token, user: response.data.user });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  } catch (error) {
    // SECURITY ISSUE: Exposing internal errors
    res.status(500).json({ error: error.message, stack: error.stack });
  }
});

// User routes
app.get('/api/users/:id', async (req, res) => {
  try {
    // SECURITY ISSUE: No authorization check
    // PERFORMANCE ISSUE: No caching
    const response = await axios.get(`${process.env.USER_SERVICE_URL}/users/${req.params.id}`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

// Product routes
app.get('/api/products', async (req, res) => {
  try {
    // PERFORMANCE ISSUE: No pagination, returns all products
    const response = await axios.get(`${process.env.PRODUCT_SERVICE_URL}/products`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

app.get('/api/products/:id', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.PRODUCT_SERVICE_URL}/products/${req.params.id}`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

// SECURITY ISSUE: SQL injection vulnerability through parameter
app.get('/api/products/search', async (req, res) => {
  try {
    const { q } = req.query;
    // Directly passing user input without validation
    const response = await axios.get(`${process.env.PRODUCT_SERVICE_URL}/products/search?q=${q}`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

// Order routes
app.post('/api/orders', async (req, res) => {
  try {
    // SECURITY ISSUE: No authentication check
    // PERFORMANCE ISSUE: Sequential calls, no error handling
    const { userId, items } = req.body;
    
    // Call order service
    const orderResponse = await axios.post(`${process.env.ORDER_SERVICE_URL}/orders`, {
      userId,
      items
    });
    
    // PERFORMANCE ISSUE: Waiting for payment synchronously
    const paymentResponse = await axios.post(`${process.env.PAYMENT_SERVICE_URL}/payments`, {
      orderId: orderResponse.data.id,
      amount: orderResponse.data.total
    });
    
    res.json({
      order: orderResponse.data,
      payment: paymentResponse.data
    });
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

app.get('/api/orders/:id', async (req, res) => {
  try {
    // SECURITY ISSUE: No ownership check
    const response = await axios.get(`${process.env.ORDER_SERVICE_URL}/orders/${req.params.id}`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

// SECURITY ISSUE: Exposed internal admin endpoint
app.delete('/api/admin/users/:id', async (req, res) => {
  try {
    // No admin role check!
    const response = await axios.delete(`${process.env.USER_SERVICE_URL}/users/${req.params.id}`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: No error handling for downstream service failures
// CODE QUALITY ISSUE: No circuit breaker pattern

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});

module.exports = app;
