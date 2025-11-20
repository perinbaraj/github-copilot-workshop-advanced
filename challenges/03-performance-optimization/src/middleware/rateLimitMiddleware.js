/**
 * Rate Limiting Middleware
 * 
 * PERFORMANCE ISSUE: In-memory rate limiting won't work in cluster
 * Should use Redis for distributed rate limiting
 */

const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('../config/redis');

/**
 * Create rate limiter
 * 
 * PERFORMANCE ISSUE: Uses in-memory store by default
 * In production, should use Redis store for cluster support
 */
function createRateLimiter(options = {}) {
  const defaults = {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
  };
  
  const config = { ...defaults, ...options };
  
  // PERFORMANCE ISSUE: In-memory store doesn't work in cluster!
  // Should use Redis store
  if (process.env.USE_REDIS_RATE_LIMIT === 'true') {
    config.store = new RedisStore({
      client: redis.client,
      prefix: 'rl:',
    });
  }
  
  return rateLimit(config);
}

// API rate limiter
const apiLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 100
});

// Strict rate limiter for expensive operations
const strictLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: 'Rate limit exceeded for this endpoint'
});

// Auth rate limiter
const authLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Too many authentication attempts, please try again later'
});

module.exports = {
  createRateLimiter,
  apiLimiter,
  strictLimiter,
  authLimiter
};
