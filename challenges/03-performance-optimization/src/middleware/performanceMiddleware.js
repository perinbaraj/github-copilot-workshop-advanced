/**
 * Performance Monitoring Middleware
 * Logs request duration and detects slow requests
 */

function performanceMiddleware(req, res, next) {
  const start = Date.now();
  
  // Store original end function
  const originalEnd = res.end;
  
  // Override end to measure duration
  res.end = function(...args) {
    const duration = Date.now() - start;
    
    // Log request info
    console.log(`${req.method} ${req.originalUrl} - ${res.statusCode} - ${duration}ms`);
    
    // Warn on slow requests
    if (duration > 1000) {
      console.warn(`SLOW REQUEST: ${req.method} ${req.originalUrl} took ${duration}ms`);
    }
    
    // Add response header
    res.setHeader('X-Response-Time', `${duration}ms`);
    
    // Call original end
    return originalEnd.apply(res, args);
  };
  
  next();
}

module.exports = performanceMiddleware;
