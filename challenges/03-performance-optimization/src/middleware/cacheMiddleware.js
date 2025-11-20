/**
 * Cache Middleware
 * 
 * PERFORMANCE ISSUE: Cache is implemented but NOT USED in routes!
 * This middleware exists but is not applied to any endpoints
 */

const redis = require('../config/redis');

/**
 * Cache middleware factory
 * 
 * @param {number} ttl - Time to live in seconds
 * @param {function} keyGenerator - Function to generate cache key from request
 */
function cacheMiddleware(ttl = 3600, keyGenerator = null) {
  return async (req, res, next) => {
    // PERFORMANCE ISSUE: Cache is implemented but not used!
    
    // Generate cache key
    const cacheKey = keyGenerator 
      ? keyGenerator(req)
      : `api:${req.method}:${req.originalUrl}`;
    
    try {
      // Check cache
      const cachedData = await redis.client.get(cacheKey);
      
      if (cachedData) {
        console.log(`Cache HIT: ${cacheKey}`);
        return res.json(JSON.parse(cachedData));
      }
      
      console.log(`Cache MISS: ${cacheKey}`);
      
      // Store original json method
      const originalJson = res.json.bind(res);
      
      // Override json method to cache response
      res.json = function(data) {
        // Cache the response
        redis.client.setEx(cacheKey, ttl, JSON.stringify(data))
          .catch(err => console.error('Cache set error:', err));
        
        // Send response
        return originalJson(data);
      };
      
      next();
    } catch (error) {
      console.error('Cache middleware error:', error);
      next(); // Continue without cache on error
    }
  };
}

/**
 * Cache invalidation middleware
 * Invalidates cache when data is modified
 */
function invalidateCacheMiddleware(pattern) {
  return async (req, res, next) => {
    // Store original json method
    const originalJson = res.json.bind(res);
    
    // Override to invalidate cache after successful response
    res.json = function(data) {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        redis.invalidatePattern(pattern)
          .catch(err => console.error('Cache invalidation error:', err));
      }
      return originalJson(data);
    };
    
    next();
  };
}

module.exports = {
  cacheMiddleware,
  invalidateCacheMiddleware
};
