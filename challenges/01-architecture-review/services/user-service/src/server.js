const express = require('express');
const bcrypt = require('bcrypt');
const { Pool } = require('pg');
const redis = require('redis');

const app = express();
const PORT = process.env.PORT || 3001;

// PERFORMANCE ISSUE: No connection pooling configuration
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD
});

// PERFORMANCE ISSUE: Redis client not properly configured
const redisClient = redis.createClient({
  socket: {
    host: process.env.REDIS_HOST,
    port: 6379
  },
  password: process.env.REDIS_PASSWORD
});

redisClient.connect().catch(console.error);

app.use(express.json());

// Initialize database
async function initDB() {
  const client = await pool.connect();
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('Database initialized');
  } finally {
    client.release();
  }
}

initDB();

// SECURITY ISSUE: Weak password hashing (low salt rounds)
app.post('/users/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName } = req.body;
    
    // SECURITY ISSUE: No input validation
    // SECURITY ISSUE: Only 4 salt rounds (should be 10+)
    const passwordHash = await bcrypt.hash(password, 4);
    
    const result = await pool.query(
      'INSERT INTO users (email, password_hash, first_name, last_name) VALUES ($1, $2, $3, $4) RETURNING id, email, first_name, last_name',
      [email, passwordHash, firstName, lastName]
    );
    
    res.status(201).json({ user: result.rows[0] });
  } catch (error) {
    // SECURITY ISSUE: Exposing database errors
    res.status(500).json({ error: error.message, detail: error.detail });
  }
});

// SECURITY ISSUE: Timing attack vulnerability
app.post('/users/authenticate', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // PERFORMANCE ISSUE: No index on email, slow query
    const result = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const user = result.rows[0];
    const isValid = await bcrypt.compare(password, user.password_hash);
    
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // SECURITY ISSUE: Returning password hash
    res.json({ user });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: N+1 query problem
app.get('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // PERFORMANCE ISSUE: No caching
    const userResult = await pool.query(
      'SELECT id, email, first_name, last_name, created_at FROM users WHERE id = $1',
      [id]
    );
    
    if (userResult.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    const user = userResult.rows[0];
    
    // PERFORMANCE ISSUE: Separate query for orders count
    const ordersResult = await pool.query(
      'SELECT COUNT(*) as order_count FROM orders WHERE user_id = $1',
      [id]
    );
    
    user.orderCount = parseInt(ordersResult.rows[0].order_count);
    
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SECURITY ISSUE: Mass assignment vulnerability
app.put('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    // SECURITY ISSUE: No validation of what fields can be updated
    // User could update any field including password_hash directly
    const fields = Object.keys(updates);
    const values = Object.values(updates);
    
    const setClause = fields.map((field, index) => `${field} = $${index + 1}`).join(', ');
    
    const result = await pool.query(
      `UPDATE users SET ${setClause} WHERE id = $${fields.length + 1} RETURNING *`,
      [...values, id]
    );
    
    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: No pagination
app.get('/users', async (req, res) => {
  try {
    // Returns ALL users - performance issue with large datasets
    const result = await pool.query(
      'SELECT id, email, first_name, last_name, created_at FROM users ORDER BY created_at DESC'
    );
    
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SECURITY ISSUE: No authorization check
app.delete('/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    await pool.query('DELETE FROM users WHERE id = $1', [id]);
    res.json({ message: 'User deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CODE QUALITY ISSUE: No graceful shutdown
app.listen(PORT, () => {
  console.log(`User service running on port ${PORT}`);
});

module.exports = app;
