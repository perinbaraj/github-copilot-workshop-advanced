#!/usr/bin/env node

/**
 * Performance Benchmark Runner
 * 
 * This script runs performance benchmarks against the StreamVibe API
 * to identify bottlenecks and measure improvements.
 */

const http = require('http');
const https = require('https');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const WARMUP_REQUESTS = 10;
const BENCHMARK_REQUESTS = 100;

class PerformanceBenchmark {
  constructor() {
    this.results = {};
  }

  async request(path) {
    return new Promise((resolve, reject) => {
      const url = `${BASE_URL}${path}`;
      const protocol = url.startsWith('https') ? https : http;
      
      const startTime = process.hrtime.bigint();
      
      protocol.get(url, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          const endTime = process.hrtime.bigint();
          const duration = Number(endTime - startTime) / 1_000_000; // Convert to ms
          
          resolve({
            statusCode: res.statusCode,
            duration,
            size: Buffer.byteLength(data, 'utf8')
          });
        });
      }).on('error', (err) => {
        reject(err);
      });
    });
  }

  async warmup(path) {
    console.log(`Warming up: ${path}`);
    for (let i = 0; i < WARMUP_REQUESTS; i++) {
      await this.request(path);
    }
  }

  async benchmarkEndpoint(name, path) {
    console.log(`\n📊 Benchmarking: ${name}`);
    console.log(`Path: ${path}`);
    
    await this.warmup(path);
    
    const durations = [];
    const errors = [];
    
    const startTime = Date.now();
    
    for (let i = 0; i < BENCHMARK_REQUESTS; i++) {
      try {
        const result = await this.request(path);
        durations.push(result.duration);
        
        if (result.statusCode !== 200) {
          errors.push(result.statusCode);
        }
      } catch (err) {
        errors.push(err.message);
      }
    }
    
    const totalTime = Date.now() - startTime;
    
    // Calculate statistics
    durations.sort((a, b) => a - b);
    
    const stats = {
      requests: BENCHMARK_REQUESTS,
      totalTime: totalTime,
      avgDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      minDuration: durations[0],
      maxDuration: durations[durations.length - 1],
      p50: durations[Math.floor(durations.length * 0.5)],
      p95: durations[Math.floor(durations.length * 0.95)],
      p99: durations[Math.floor(durations.length * 0.99)],
      requestsPerSecond: (BENCHMARK_REQUESTS / totalTime) * 1000,
      errorRate: (errors.length / BENCHMARK_REQUESTS) * 100,
      errors: errors.length
    };
    
    this.results[name] = stats;
    
    // Print results
    console.log(`\nResults:`);
    console.log(`  Total Time: ${totalTime.toFixed(0)}ms`);
    console.log(`  Avg Duration: ${stats.avgDuration.toFixed(2)}ms`);
    console.log(`  Min Duration: ${stats.minDuration.toFixed(2)}ms`);
    console.log(`  Max Duration: ${stats.maxDuration.toFixed(2)}ms`);
    console.log(`  P50: ${stats.p50.toFixed(2)}ms`);
    console.log(`  P95: ${stats.p95.toFixed(2)}ms`);
    console.log(`  P99: ${stats.p99.toFixed(2)}ms`);
    console.log(`  Requests/sec: ${stats.requestsPerSecond.toFixed(2)}`);
    console.log(`  Error Rate: ${stats.errorRate.toFixed(2)}%`);
    
    return stats;
  }

  async runAllBenchmarks() {
    console.log('🚀 Starting Performance Benchmarks\n');
    console.log('=' .repeat(60));
    
    // Benchmark different endpoints
    await this.benchmarkEndpoint(
      'Video List (No Pagination)',
      '/api/videos'
    );
    
    await this.benchmarkEndpoint(
      'Video Details (N+1 Queries)',
      '/api/videos/1'
    );
    
    await this.benchmarkEndpoint(
      'Video Page (Sequential Queries)',
      '/api/videos/1/page'
    );
    
    await this.benchmarkEndpoint(
      'Search (No Index)',
      '/api/search?q=tutorial'
    );
    
    await this.benchmarkEndpoint(
      'Recommendations (O(n²) Algorithm)',
      '/api/recommendations/1'
    );
    
    // Print summary
    this.printSummary();
  }

  printSummary() {
    console.log('\n' + '=' .repeat(60));
    console.log('📈 Performance Summary\n');
    
    const sortedResults = Object.entries(this.results)
      .sort((a, b) => b[1].avgDuration - a[1].avgDuration);
    
    console.log('Endpoints by Average Response Time (Slowest First):\n');
    
    sortedResults.forEach(([name, stats], index) => {
      const status = stats.avgDuration > 1000 ? '🔴' : 
                     stats.avgDuration > 500 ? '🟡' : '🟢';
      
      console.log(`${index + 1}. ${status} ${name}`);
      console.log(`   Avg: ${stats.avgDuration.toFixed(2)}ms | P95: ${stats.p95.toFixed(2)}ms | RPS: ${stats.requestsPerSecond.toFixed(2)}`);
    });
    
    // Identify critical issues
    console.log('\n⚠️  Critical Performance Issues:\n');
    
    Object.entries(this.results).forEach(([name, stats]) => {
      if (stats.avgDuration > 1000) {
        console.log(`  • ${name}: Avg response time ${stats.avgDuration.toFixed(0)}ms (Target: <500ms)`);
      }
      if (stats.p95 > 2000) {
        console.log(`  • ${name}: P95 ${stats.p95.toFixed(0)}ms (Target: <1000ms)`);
      }
      if (stats.errorRate > 5) {
        console.log(`  • ${name}: Error rate ${stats.errorRate.toFixed(1)}% (Target: <1%)`);
      }
    });
    
    console.log('\n' + '=' .repeat(60));
  }
}

// Run benchmarks
const benchmark = new PerformanceBenchmark();
benchmark.runAllBenchmarks()
  .then(() => {
    console.log('\n✅ Benchmarks completed!');
    process.exit(0);
  })
  .catch((err) => {
    console.error('❌ Benchmark failed:', err);
    process.exit(1);
  });
