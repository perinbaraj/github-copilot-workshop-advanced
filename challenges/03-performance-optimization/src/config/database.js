/**
 * Database Configuration
 * 
 * PERFORMANCE ISSUES:
 * 1. Small connection pool (max: 5)
 * 2. No read replica configuration
 * 3. No connection pool monitoring
 * 4. Default timeout settings
 * 5. No query logging for slow queries
 */

const { Pool } = require('pg');

// PERFORMANCE ISSUE: Small connection pool
// Default max: 5 connections is too small for production
// With 100 concurrent requests, most will wait for connections
const pgConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'streamvibe',
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || 'admin123',
  
  // Connection pool settings
  max: parseInt(process.env.DB_POOL_MAX) || 5, // PERFORMANCE ISSUE: Too small!
  min: parseInt(process.env.DB_POOL_MIN) || 2,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  
  // PERFORMANCE ISSUE: No statement timeout
  // Long-running queries can block the pool
  // statement_timeout: 30000, // Should be set!
  
  // Query timeout
  query_timeout: 10000,
  
  // Keep-alive
  keepAlive: true,
  keepAliveInitialDelayMillis: 10000,
};

const pool = new Pool(pgConfig);

// PERFORMANCE ISSUE: No pool event monitoring
// Should monitor 'error', 'connect', 'acquire', 'remove' events
pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

pool.on('connect', (client) => {
  console.log('New database connection established');
});

// PERFORMANCE ISSUE: No slow query logging
// Should log queries that take > 100ms

/**
 * Execute query with timing
 * PERFORMANCE MONITORING: Basic query timing
 */
async function query(text, params) {
  const start = Date.now();
  try {
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    
    // Log slow queries
    if (duration > 100) {
      console.warn(`Slow query (${duration}ms):`, text.substring(0, 100));
    }
    
    return res;
  } catch (error) {
    const duration = Date.now() - start;
    console.error(`Query error (${duration}ms):`, error.message);
    throw error;
  }
}

/**
 * Get pool status
 * Useful for monitoring connection pool health
 */
function getPoolStatus() {
  return {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount,
  };
}

module.exports = {
  pool,
  query,
  getPoolStatus
};
