/**
 * Environment Configuration
 * Central configuration for the application
 */

require('dotenv').config();

module.exports = {
  // Server
  port: parseInt(process.env.PORT) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // Database
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT) || 5432,
    name: process.env.DB_NAME || 'streamvibe',
    user: process.env.DB_USER || 'admin',
    password: process.env.DB_PASSWORD || 'admin123',
    poolMax: parseInt(process.env.DB_POOL_MAX) || 5,
    poolMin: parseInt(process.env.DB_POOL_MIN) || 2,
    logging: process.env.DB_LOGGING === 'true'
  },
  
  // Redis
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT) || 6379,
    password: process.env.REDIS_PASSWORD,
    db: parseInt(process.env.REDIS_DB) || 0
  },
  
  // Cache
  cache: {
    enabled: process.env.CACHE_ENABLED === 'true',
    defaultTTL: parseInt(process.env.CACHE_DEFAULT_TTL) || 3600,
    videoTTL: parseInt(process.env.CACHE_VIDEO_TTL) || 1800,
    feedTTL: parseInt(process.env.CACHE_FEED_TTL) || 300,
    searchTTL: parseInt(process.env.CACHE_SEARCH_TTL) || 600
  },
  
  // Rate limiting
  rateLimit: {
    enabled: process.env.RATE_LIMIT_ENABLED === 'true',
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 900000, // 15 min
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    useRedis: process.env.USE_REDIS_RATE_LIMIT === 'true'
  },
  
  // APM
  apm: {
    enabled: process.env.APM_ENABLED === 'true',
    type: process.env.APM_TYPE || 'elastic',
    serviceName: process.env.APM_SERVICE_NAME || 'streamvibe-api',
    sampleRate: parseFloat(process.env.APM_SAMPLE_RATE) || 1.0
  },
  
  // Pagination
  pagination: {
    defaultLimit: parseInt(process.env.PAGINATION_DEFAULT_LIMIT) || 20,
    maxLimit: parseInt(process.env.PAGINATION_MAX_LIMIT) || 100
  }
};
