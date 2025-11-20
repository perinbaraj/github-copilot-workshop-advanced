/**
 * Redis Configuration
 * 
 * PERFORMANCE ISSUES:
 * 1. Redis configured but not used in application
 * 2. No connection retry logic
 * 3. No cluster configuration for scale
 * 4. No cache warming strategy
 */

const redis = require('redis');

const redisConfig = {
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  db: process.env.REDIS_DB || 0,
  
  // PERFORMANCE ISSUE: No retry strategy
  // Should implement exponential backoff
  retry_strategy: function(options) {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      return new Error('Redis connection refused');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      return new Error('Redis retry time exhausted');
    }
    if (options.attempt > 10) {
      return undefined;
    }
    return Math.min(options.attempt * 100, 3000);
  },
  
  // Socket keep-alive
  socket_keepalive: true,
  socket_initial_delay: 0
};

const client = redis.createClient(redisConfig);

client.on('error', (err) => {
  console.error('Redis Client Error:', err);
});

client.on('connect', () => {
  console.log('Redis connected successfully');
});

client.on('ready', () => {
  console.log('Redis client ready');
});

client.on('reconnecting', () => {
  console.log('Redis client reconnecting...');
});

/**
 * Connect to Redis
 */
async function connect() {
  try {
    await client.connect();
    console.log('Redis connection established');
  } catch (error) {
    console.error('Failed to connect to Redis:', error);
    throw error;
  }
}

/**
 * Get cache with fallback
 */
async function getWithFallback(key, fallbackFn, ttl = 3600) {
  try {
    const cached = await client.get(key);
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (error) {
    console.error('Redis get error:', error);
  }
  
  // Cache miss or error - execute fallback
  const data = await fallbackFn();
  
  // Set cache asynchronously
  try {
    await client.setEx(key, ttl, JSON.stringify(data));
  } catch (error) {
    console.error('Redis set error:', error);
  }
  
  return data;
}

/**
 * Invalidate cache by pattern
 */
async function invalidatePattern(pattern) {
  try {
    const keys = await client.keys(pattern);
    if (keys.length > 0) {
      await client.del(keys);
    }
  } catch (error) {
    console.error('Redis invalidate error:', error);
  }
}

module.exports = {
  client,
  connect,
  getWithFallback,
  invalidatePattern
};
