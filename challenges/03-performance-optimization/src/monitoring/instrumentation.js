/**
 * Application Performance Monitoring (APM) Instrumentation
 * 
 * PERFORMANCE ISSUE: APM configured but not initialized!
 * This file exists but APM is never started
 */

// Note: This would require installing APM agent
// npm install elastic-apm-node (for Elastic APM)
// npm install newrelic (for New Relic)
// npm install @opentelemetry/sdk-node (for OpenTelemetry)

/**
 * Initialize APM agent
 * 
 * PERFORMANCE ISSUE: Not called in server.js!
 */
function initializeAPM() {
  if (process.env.APM_ENABLED !== 'true') {
    console.log('APM is disabled');
    return null;
  }
  
  const apmType = process.env.APM_TYPE || 'elastic';
  
  try {
    switch (apmType) {
      case 'elastic':
        return initializeElasticAPM();
      case 'newrelic':
        return initializeNewRelic();
      case 'opentelemetry':
        return initializeOpenTelemetry();
      default:
        console.warn(`Unknown APM type: ${apmType}`);
        return null;
    }
  } catch (error) {
    console.error('Failed to initialize APM:', error);
    return null;
  }
}

/**
 * Initialize Elastic APM
 */
function initializeElasticAPM() {
  const apm = require('elastic-apm-node').start({
    serviceName: process.env.APM_SERVICE_NAME || 'streamvibe-api',
    serverUrl: process.env.ELASTIC_APM_SERVER_URL,
    secretToken: process.env.ELASTIC_APM_SECRET_TOKEN,
    environment: process.env.NODE_ENV || 'development',
    
    // Transaction sample rate
    transactionSampleRate: parseFloat(process.env.APM_SAMPLE_RATE) || 1.0,
    
    // Capture request body
    captureBody: 'all',
    
    // Error handling
    captureErrorLogStackTraces: 'always',
    
    // Performance
    metricsInterval: '30s',
  });
  
  console.log('Elastic APM initialized');
  return apm;
}

/**
 * Initialize New Relic
 */
function initializeNewRelic() {
  const newrelic = require('newrelic');
  console.log('New Relic initialized');
  return newrelic;
}

/**
 * Initialize OpenTelemetry
 */
function initializeOpenTelemetry() {
  const { NodeSDK } = require('@opentelemetry/sdk-node');
  const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
  
  const sdk = new NodeSDK({
    serviceName: process.env.OTEL_SERVICE_NAME || 'streamvibe-api',
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-fs': {
          enabled: false,
        },
      }),
    ],
  });
  
  sdk.start();
  console.log('OpenTelemetry initialized');
  
  return sdk;
}

/**
 * Custom transaction tracking
 */
function trackTransaction(name, type = 'custom') {
  const start = Date.now();
  
  return {
    end: (metadata = {}) => {
      const duration = Date.now() - start;
      console.log(`Transaction: ${name} (${type}) - ${duration}ms`, metadata);
      
      // In production, this would send to APM
    }
  };
}

/**
 * Track slow database queries
 */
function trackSlowQuery(query, duration, params = {}) {
  if (duration > 100) {
    console.warn('Slow Query:', {
      query: query.substring(0, 100),
      duration: `${duration}ms`,
      params
    });
    
    // In production, send to APM
  }
}

module.exports = {
  initializeAPM,
  trackTransaction,
  trackSlowQuery
};
