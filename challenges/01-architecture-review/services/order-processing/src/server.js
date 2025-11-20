const express = require('express');
const { Pool } = require('pg');
const amqp = require('amqplib');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3003;

// PERFORMANCE ISSUE: No connection pooling configuration
const pool = new Pool({
  host: process.env.DB_HOST || 'postgres',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'techmart',
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || 'password123'
});

let rabbitChannel;

app.use(express.json());

// Initialize database
async function initDB() {
  const client = await pool.connect();
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    await client.query(`
      CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_id VARCHAR(255) NOT NULL,
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL
      )
    `);
    
    console.log('Database initialized');
  } finally {
    client.release();
  }
}

// PERFORMANCE ISSUE: Synchronous RabbitMQ connection
async function initRabbitMQ() {
  try {
    const connection = await amqp.connect(process.env.RABBITMQ_URL || 'amqp://admin:password123@rabbitmq:5672');
    rabbitChannel = await connection.createChannel();
    await rabbitChannel.assertQueue('orders');
    console.log('RabbitMQ initialized');
  } catch (error) {
    console.error('RabbitMQ connection failed:', error);
  }
}

initDB();
initRabbitMQ();

// SECURITY ISSUE: No authentication check
// ARCHITECTURE ISSUE: Should be async with saga pattern
app.post('/orders', async (req, res) => {
  try {
    const { userId, items } = req.body;
    
    // SECURITY ISSUE: No input validation
    // ARCHITECTURE ISSUE: No transaction handling
    
    // Calculate total
    let totalAmount = 0;
    for (const item of items) {
      // PERFORMANCE ISSUE: N+1 query problem - calling product service for each item
      const productResponse = await axios.get(`${process.env.PRODUCT_SERVICE_URL || 'http://product-catalog:3002'}/products/${item.productId}`);
      const product = productResponse.data;
      totalAmount += product.price * item.quantity;
    }
    
    // Create order
    const orderResult = await pool.query(
      'INSERT INTO orders (user_id, total_amount) VALUES ($1, $2) RETURNING id',
      [userId, totalAmount]
    );
    
    const orderId = orderResult.rows[0].id;
    
    // Insert order items
    for (const item of items) {
      // PERFORMANCE ISSUE: Individual inserts instead of batch
      const productResponse = await axios.get(`${process.env.PRODUCT_SERVICE_URL || 'http://product-catalog:3002'}/products/${item.productId}`);
      const product = productResponse.data;
      
      await pool.query(
        'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)',
        [orderId, item.productId, item.quantity, product.price]
      );
    }
    
    // ARCHITECTURE ISSUE: Synchronous payment processing - should be async
    try {
      await axios.post(`${process.env.PAYMENT_SERVICE_URL || 'http://payment-gateway:5000'}/payments/process`, {
        orderId,
        amount: totalAmount,
        userId
      });
    } catch (error) {
      // ARCHITECTURE ISSUE: No rollback mechanism
      console.error('Payment failed:', error);
      await pool.query('UPDATE orders SET status = $1 WHERE id = $2', ['payment_failed', orderId]);
      return res.status(400).json({ error: 'Payment processing failed' });
    }
    
    // Publish to message queue
    if (rabbitChannel) {
      rabbitChannel.sendToQueue('orders', Buffer.from(JSON.stringify({ orderId, userId, totalAmount })));
    }
    
    res.status(201).json({ orderId, totalAmount, status: 'completed' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: No caching
app.get('/orders/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // SECURITY ISSUE: No ownership check
    const orderResult = await pool.query('SELECT * FROM orders WHERE id = $1', [id]);
    
    if (orderResult.rows.length === 0) {
      return res.status(404).json({ error: 'Order not found' });
    }
    
    const order = orderResult.rows[0];
    
    // PERFORMANCE ISSUE: N+1 query
    const itemsResult = await pool.query('SELECT * FROM order_items WHERE order_id = $1', [id]);
    order.items = itemsResult.rows;
    
    res.json(order);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: No pagination
app.get('/users/:userId/orders', async (req, res) => {
  try {
    const { userId } = req.params;
    
    const result = await pool.query('SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC', [userId]);
    
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CODE QUALITY ISSUE: No graceful shutdown
app.listen(PORT, () => {
  console.log(`Order Processing service running on port ${PORT}`);
});

module.exports = app;
