const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');
const redis = require('redis');

const app = express();
const PORT = process.env.PORT || 3002;

// PERFORMANCE ISSUE: No connection pooling configuration for MongoDB
const mongoUrl = process.env.MONGODB_URI || 'mongodb://admin:password123@mongodb:27017/products?authSource=admin';
let db;

// PERFORMANCE ISSUE: Redis client not properly configured
const redisClient = redis.createClient({
  socket: {
    host: process.env.REDIS_HOST || 'redis',
    port: 6379
  },
  password: process.env.REDIS_PASSWORD
});

redisClient.connect().catch(console.error);

app.use(express.json());

// Initialize database
async function initDB() {
  try {
    const client = await MongoClient.connect(mongoUrl);
    db = client.db('products');
    
    // Create sample products
    const productsCollection = db.collection('products');
    const count = await productsCollection.countDocuments();
    
    if (count === 0) {
      await productsCollection.insertMany([
        {
          name: 'Laptop Pro',
          description: 'High-performance laptop',
          price: 1299.99,
          category: 'Electronics',
          stock: 50,
          tags: ['laptop', 'computer', 'electronics']
        },
        {
          name: 'Wireless Mouse',
          description: 'Ergonomic wireless mouse',
          price: 29.99,
          category: 'Accessories',
          stock: 200,
          tags: ['mouse', 'wireless', 'accessories']
        },
        {
          name: 'USB-C Cable',
          description: 'Fast charging USB-C cable',
          price: 15.99,
          category: 'Accessories',
          stock: 500,
          tags: ['cable', 'usb-c', 'charging']
        }
      ]);
      console.log('Sample products created');
    }
    
    console.log('Database initialized');
  } catch (error) {
    console.error('Database initialization failed:', error);
  }
}

initDB();

// PERFORMANCE ISSUE: No pagination on list endpoint
// PERFORMANCE ISSUE: No caching
app.get('/products', async (req, res) => {
  try {
    const products = await db.collection('products').find({}).toArray();
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/products/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // SECURITY ISSUE: No input validation
    const product = await db.collection('products').findOne({ _id: new ObjectId(id) });
    
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    
    res.json(product);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SECURITY ISSUE: No input validation
// PERFORMANCE ISSUE: Text search without proper indexing
app.get('/products/search', async (req, res) => {
  try {
    const { query } = req.query;
    
    // SECURITY ISSUE: Potential NoSQL injection
    const products = await db.collection('products').find({
      $or: [
        { name: { $regex: query, $options: 'i' } },
        { description: { $regex: query, $options: 'i' } }
      ]
    }).toArray();
    
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SECURITY ISSUE: No authentication check
app.post('/products', async (req, res) => {
  try {
    const { name, description, price, category, stock } = req.body;
    
    // SECURITY ISSUE: No input validation
    const result = await db.collection('products').insertOne({
      name,
      description,
      price,
      category,
      stock,
      createdAt: new Date()
    });
    
    res.status(201).json({ id: result.insertedId });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// SECURITY ISSUE: No authentication/authorization
app.put('/products/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    // SECURITY ISSUE: Mass assignment vulnerability
    await db.collection('products').updateOne(
      { _id: new ObjectId(id) },
      { $set: updates }
    );
    
    res.json({ message: 'Product updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CODE QUALITY ISSUE: No graceful shutdown
app.listen(PORT, () => {
  console.log(`Product Catalog running on port ${PORT}`);
});

module.exports = app;
