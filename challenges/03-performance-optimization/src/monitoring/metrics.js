/**
 * Metrics Collection
 * Track application metrics for monitoring
 */

class MetricsCollector {
  constructor() {
    this.metrics = {
      requests: {
        total: 0,
        success: 0,
        error: 0,
        byEndpoint: {}
      },
      latency: {
        p50: 0,
        p95: 0,
        p99: 0,
        samples: []
      },
      database: {
        queries: 0,
        slowQueries: 0,
        errors: 0
      },
      cache: {
        hits: 0,
        misses: 0,
        hitRate: 0
      }
    };
  }
  
  /**
   * Record request
   */
  recordRequest(endpoint, duration, statusCode) {
    this.metrics.requests.total++;
    
    if (statusCode >= 200 && statusCode < 400) {
      this.metrics.requests.success++;
    } else {
      this.metrics.requests.error++;
    }
    
    // Track by endpoint
    if (!this.metrics.requests.byEndpoint[endpoint]) {
      this.metrics.requests.byEndpoint[endpoint] = {
        count: 0,
        avgDuration: 0,
        totalDuration: 0
      };
    }
    
    const endpointMetrics = this.metrics.requests.byEndpoint[endpoint];
    endpointMetrics.count++;
    endpointMetrics.totalDuration += duration;
    endpointMetrics.avgDuration = endpointMetrics.totalDuration / endpointMetrics.count;
    
    // Record latency sample
    this.metrics.latency.samples.push(duration);
    
    // Keep only last 1000 samples
    if (this.metrics.latency.samples.length > 1000) {
      this.metrics.latency.samples.shift();
    }
    
    this.updateLatencyPercentiles();
  }
  
  /**
   * Update latency percentiles
   */
  updateLatencyPercentiles() {
    const sorted = [...this.metrics.latency.samples].sort((a, b) => a - b);
    const len = sorted.length;
    
    if (len > 0) {
      this.metrics.latency.p50 = sorted[Math.floor(len * 0.5)];
      this.metrics.latency.p95 = sorted[Math.floor(len * 0.95)];
      this.metrics.latency.p99 = sorted[Math.floor(len * 0.99)];
    }
  }
  
  /**
   * Record database query
   */
  recordQuery(duration) {
    this.metrics.database.queries++;
    
    if (duration > 100) {
      this.metrics.database.slowQueries++;
    }
  }
  
  /**
   * Record cache hit/miss
   */
  recordCacheHit() {
    this.metrics.cache.hits++;
    this.updateCacheHitRate();
  }
  
  recordCacheMiss() {
    this.metrics.cache.misses++;
    this.updateCacheHitRate();
  }
  
  updateCacheHitRate() {
    const total = this.metrics.cache.hits + this.metrics.cache.misses;
    this.metrics.cache.hitRate = total > 0 
      ? (this.metrics.cache.hits / total) * 100 
      : 0;
  }
  
  /**
   * Get current metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      timestamp: new Date().toISOString()
    };
  }
  
  /**
   * Reset metrics
   */
  reset() {
    this.metrics.requests.total = 0;
    this.metrics.requests.success = 0;
    this.metrics.requests.error = 0;
    this.metrics.requests.byEndpoint = {};
    this.metrics.latency.samples = [];
    this.metrics.database.queries = 0;
    this.metrics.database.slowQueries = 0;
    this.metrics.cache.hits = 0;
    this.metrics.cache.misses = 0;
  }
}

// Singleton instance
const metricsCollector = new MetricsCollector();

module.exports = metricsCollector;
