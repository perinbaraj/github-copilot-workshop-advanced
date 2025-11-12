# Challenge 3: Performance Optimization - StreamVibe

## 📊 Scenario

You've inherited **StreamVibe**, a video streaming platform experiencing severe performance issues:

- API endpoints timing out under load
- Database queries taking 5-10 seconds
- Memory leaks causing crashes
- Poor user experience

**Your Mission:** Use GitHub Copilot agents to identify bottlenecks, propose optimizations, and implement performance improvements.

## 🎯 Learning Objectives

1. **Performance Profiling** - Identify N+1 queries, missing indexes, inefficient algorithms
2. **Database Optimization** - Add indexes, optimize queries, implement caching
3. **Caching Strategies** - Implement Redis caching effectively
4. **Algorithm Efficiency** - Refactor O(n²) to O(n log n) or O(n)
5. **Concurrent Operations** - Parallelize independent operations
4. **Code-Level Optimization** - Algorithmic improvements, async patterns
5. **Load Testing** - Creating realistic performance tests
6. **Monitoring & Observability** - Instrumenting for performance visibility
7. **Cost Optimization** - Reducing infrastructure spend through efficiency

---

## 🛠️ Copilot Skills You'll Practice

- **Performance Engineer Agent**: Identifying bottlenecks and optimization opportunities
- **Database Architect Agent**: Query optimization and schema design
- **Caching Expert Agent**: Designing multi-layer caching strategies
- **DevOps Agent**: Infrastructure and scaling recommendations
- **Code Reviewer Agent**: Finding inefficient algorithms and patterns

---

## 📋 Prerequisites

- GitHub Copilot Chat with agent mode
- VS Code with Copilot extensions
- Node.js 18+, React
- PostgreSQL, MongoDB, Redis
- Docker & Docker Compose
- Load testing tools (k6, Artillery)
- Performance monitoring tools (understanding of)

---

## 🚀 Getting Started

## 🚀 Getting Started

### Prerequisites
- Docker Desktop installed
- Node.js 16+ installed
- GitHub Copilot with agent mode enabled

### Setup

1. **Start the database services:**
   ```bash
   cd challenges/03-performance-optimization
   docker-compose up -d
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the application:**
   ```bash
   npm start
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:3000/api/videos
   ```

## 🔍 Known Performance Issues

The codebase contains **intentional performance bottlenecks**:

### 1. N+1 Query Problem
- `GET /api/videos/:id` - Makes 5 separate queries for one video
- `GET /api/videos` - Makes additional queries for each video in the list

### 2. Missing Database Indexes
- No index on `videos.user_id`
- No index on `videos.created_at`
- No composite index on `views(video_id, user_id)`
- No indexes on `comments.video_id`, `likes.video_id`

### 3. Inefficient Search
- `GET /api/search` uses `LIKE` without full-text search
- No search index configured

### 4. Expensive Recommendation Algorithm
- `GET /api/recommendations/:userId` loads ALL videos into memory
- O(n²) similarity calculation
- No caching of results

### 5. No Caching
- Redis is configured but never used
- Every request hits the database
- No response caching

### 6. No Pagination
- `GET /api/videos` returns ALL videos (100k+ records)
- No limit or offset parameters

### 7. Sequential Operations
- `GET /api/videos/:id/page` executes 4 independent queries sequentially
- Could be parallelized

### 8. No Connection Pool Tuning
- PostgreSQL pool uses default settings
- MongoDB creates new connections on each request

**Deliverable**: `reports/BASELINE_PERFORMANCE.md` - Document current state

---

## 🔍 Performance Optimization Tasks

### Task 1: Performance Profiling & Bottleneck Identification (20-25 minutes)

**Objective**: Use a Performance Engineer agent to systematically identify all bottlenecks.

#### Step 1.1: Create Performance Engineer Agent

```
You are a senior performance engineer with expertise in:
- Application performance monitoring (APM)
- Database query optimization
- Caching architecture design
- Microservices performance patterns
- Load testing and capacity planning
- Cost optimization for cloud infrastructure

Analyze this video streaming platform's performance characteristics.
Identify bottlenecks in API endpoints, database queries, caching, and infrastructure.
Provide data-driven optimization recommendations with expected impact.
```

#### Step 1.2: API Endpoint Performance Analysis

**Agent Task**: Analyze each critical endpoint

**Critical Endpoints to Profile**:
```
1. GET /api/videos/:id - Video details page (most frequent)
2. GET /api/videos/feed - User's personalized feed
3. GET /api/search - Video search
4. POST /api/videos/:id/view - Record video view
5. GET /api/recommendations - Recommendation engine
6. GET /api/users/:id/profile - User profile
7. POST /api/videos/upload - Video upload
8. GET /api/videos/:id/comments - Comments loading
```

**For Each Endpoint, Ask Agent**:
```
Analyze the endpoint /api/videos/:id:
1. Current response time (p50, p95, p99)
2. Database queries executed (count and duration)
3. External API calls
4. Synchronous vs asynchronous operations
5. Caching opportunities
6. N+1 query problems
7. Serialization overhead
8. Expected improvement with optimizations

File: src/api/controllers/videoController.js
```

**Deliverable**: `reports/API_PERFORMANCE_ANALYSIS.md`

#### Step 1.3: Database Performance Analysis

**Create Database Architect Agent**:
```
You are a database performance expert specializing in:
- PostgreSQL and MongoDB query optimization
- Index strategy and design
- Database schema denormalization
- Connection pooling and configuration
- Query plan analysis (EXPLAIN)
- Database scaling strategies

Analyze database performance and identify optimization opportunities.
```

**Agent Tasks**:
```
1. Review slow query log (queries >100ms)
2. Analyze EXPLAIN plans for top 20 queries
3. Identify missing indexes
4. Find N+1 query patterns in codebase
5. Check table statistics and bloat
6. Evaluate connection pool configuration
7. Identify opportunities for read replicas
8. Recommend partitioning strategies

Database: videos, users, comments, likes, views, recommendations
```

**Deliverable**: `reports/DATABASE_ANALYSIS.md`

#### Step 1.4: Caching Opportunity Analysis

**Create Caching Expert Agent**:
```
You are a caching architecture expert with deep knowledge of:
- Multi-layer caching strategies (CDN, Redis, application cache)
- Cache invalidation patterns
- Cache-aside vs read-through strategies
- TTL optimization
- Cache stampede prevention
- Distributed caching with Redis Cluster

Identify caching opportunities in this streaming platform.
```

**Agent Analysis**:
```
For each data type, recommend caching strategy:
1. Video metadata (title, description, thumbnail URL)
2. User profiles
3. Video recommendations
4. Search results
5. Comments (recent comments per video)
6. Like counts and view counts
7. Trending videos list
8. User's feed (personalized content)

Consider:
- Read/write ratio
- Data freshness requirements
- Cache invalidation complexity
- Memory constraints
- Cache hit rate potential
```

**Deliverable**: `reports/CACHING_STRATEGY.md`

#### Step 1.5: Code-Level Performance Issues

**Agent Task**: Review application code for inefficiencies

```
Analyze the codebase for performance anti-patterns:
1. Blocking I/O in request handlers
2. Inefficient algorithms (O(n²) where O(n log n) possible)
3. Unnecessary data serialization
4. Memory leaks
5. CPU-intensive operations on main thread
6. Unoptimized loops and iterations
7. Excessive object creation
8. Poor async/await patterns

Focus on:
- src/api/controllers/
- src/services/
- src/models/
- src/utils/
```

**Deliverable**: `reports/CODE_PERFORMANCE_ISSUES.md`

#### Success Criteria:
- [ ] All critical endpoints profiled
- [ ] Database bottlenecks identified with query plans
- [ ] Caching strategy designed
- [ ] Code-level issues documented
- [ ] Performance improvement estimates provided

---

### Task 2: Database Query Optimization (25-30 minutes)

**Objective**: Optimize slow database queries and add missing indexes.

#### Step 2.1: Fix N+1 Query Problem in Video Feed

**Current Problem** (`src/api/controllers/feedController.js`):
```javascript
async getUserFeed(userId) {
  const videos = await Video.findAll({ limit: 20 });
  
  // N+1 problem: 20 additional queries!
  for (const video of videos) {
    video.user = await User.findById(video.userId);
    video.likeCount = await Like.count({ videoId: video.id });
    video.commentCount = await Comment.count({ videoId: video.id });
  }
  
  return videos;
}
```

**Agent Prompt**:
```
This function has an N+1 query problem. Help me:
1. Rewrite using eager loading/joins
2. Optimize to execute in 1-2 queries instead of 21+
3. Add appropriate indexes
4. Measure performance improvement
5. Write tests to ensure functionality preserved
```

**Expected Improvement**: 20 queries → 2 queries, 2000ms → 50ms

**Deliverable**: Optimized code + migration for indexes

#### Step 2.2: Optimize Video Search Query

**Current Problem** (`src/api/controllers/searchController.js`):
```javascript
async searchVideos(query) {
  // Full table scan! No indexes!
  const results = await Video.query()
    .where('title', 'LIKE', `%${query}%`)
    .orWhere('description', 'LIKE', `%${query}%`)
    .orWhere('tags', 'LIKE', `%${query}%`)
    .limit(50);
  
  return results;
}
```

**Agent Prompt**:
```
This search is extremely slow (3+ seconds). Help me:
1. Add full-text search index (PostgreSQL's tsvector or Elasticsearch)
2. Implement search with proper ranking
3. Add query caching
4. Handle typos and fuzzy matching
5. Paginate results efficiently
6. Benchmark before/after
```

**Expected Improvement**: 3000ms → 100ms, better relevance

**Deliverable**: Search implementation + Elasticsearch integration

#### Step 2.3: Add Strategic Database Indexes

**Agent Task**: Generate index migration

```
Based on the slow query log and EXPLAIN analysis, create indexes for:
1. videos.user_id (foreign key, frequently joined)
2. videos.created_at (DESC) - for sorting recent videos
3. comments.video_id, comments.created_at - for comment loading
4. likes.video_id, likes.user_id - composite for like checks
5. views.video_id, views.created_at - for analytics
6. users.email - for login queries

For each index:
- Explain why it's needed
- Show the query it optimizes
- Estimate size and performance impact
```

**Deliverable**: `migrations/add_performance_indexes.sql`

#### Step 2.4: Optimize Aggregation Queries

**Current Problem** (View count calculation):
```javascript
async getVideoStats(videoId) {
  const views = await View.count({ where: { videoId } });
  const likes = await Like.count({ where: { videoId } });
  const comments = await Comment.count({ where: { videoId } });
  
  return { views, likes, comments };
}
```

**Agent Prompt**:
```
This runs 3 separate COUNT queries. Optimize by:
1. Using materialized views or cached counters
2. Update counters incrementally (denormalization)
3. Use Redis sorted sets for real-time counts
4. Background job to sync counts periodically
5. Compare trade-offs: accuracy vs performance
```

**Expected Improvement**: 3 queries → 1 Redis GET, 300ms → 2ms

**Deliverable**: Counter caching implementation

#### Success Criteria:
- [ ] N+1 queries eliminated (measured)
- [ ] Search optimized with full-text indexing
- [ ] Strategic indexes added and benchmarked
- [ ] Aggregation queries cached
- [ ] Database query time reduced by >70%

---

### Task 3: Implement Multi-Layer Caching (25-30 minutes)

**Objective**: Implement comprehensive caching strategy to reduce database load and improve response times.

#### Step 3.1: Video Metadata Caching (Redis)

**Agent Guidance**:
```
Implement caching for video metadata:
1. Cache video details (title, thumbnail, duration, etc.)
2. TTL: 1 hour (videos rarely change)
3. Cache invalidation: on video update/delete
4. Cache warming: pre-cache trending videos
5. Cache-aside pattern implementation
6. Handle cache stampede (use locks)

Files to modify:
- src/services/videoService.js
- src/cache/videoCache.js
```

**Implementation**:
```javascript
// Example structure
class VideoCache {
  async get(videoId) {
    // Try cache first
    let video = await redis.get(`video:${videoId}`);
    if (video) return JSON.parse(video);
    
    // Cache miss: get from DB and cache
    video = await Video.findById(videoId);
    await redis.setex(`video:${videoId}`, 3600, JSON.stringify(video));
    return video;
  }
  
  async invalidate(videoId) {
    await redis.del(`video:${videoId}`);
  }
}
```

**Expected Impact**: 80%+ cache hit rate, database load -60%

#### Step 3.2: User Feed Caching (Redis)

**Agent Task**:
```
Implement personalized feed caching:
1. Cache user's feed (video IDs in order)
2. TTL: 15 minutes (balance freshness vs performance)
3. Lazy loading: cache on first access
4. Background refresh: update cache before expiry
5. Partial cache: cache video IDs, fetch metadata separately
6. Invalidation: when user follows/unfollows someone
```

**Expected Impact**: Feed loading 2000ms → 50ms

#### Step 3.3: Application-Level Response Caching

**Agent Guidance**:
```
Implement HTTP response caching for API endpoints:
1. GET /api/videos/trending - cache for 5 minutes
2. GET /api/videos/:id - cache for 1 hour with ETag
3. GET /api/search?q=... - cache search results for 10 minutes
4. Use appropriate HTTP cache headers (Cache-Control, ETag)
5. Implement conditional requests (If-None-Match)
```

**Deliverable**: Caching middleware

#### Step 3.4: CDN Integration for Static Assets

**Agent Task**:
```
Optimize static asset delivery:
1. Move video files to CDN (CloudFront, CloudFlare)
2. Generate signed URLs for access control
3. Implement adaptive bitrate streaming (HLS/DASH)
4. Cache video thumbnails on CDN
5. Set optimal cache headers (1 year for immutable assets)
6. Implement cache purging on video deletion
```

**Expected Impact**: Video delivery latency -80%, bandwidth costs -50%

#### Step 3.5: Query Result Caching

**Agent Guidance**:
```
Implement caching for expensive queries:
1. Recommendations: cache per user for 1 hour
2. Trending videos: cache globally for 5 minutes
3. Popular searches: cache search results for 30 minutes
4. User profiles: cache for 10 minutes
5. Implement cache warming for popular content
```

**Deliverable**: `src/cache/queryCacheMiddleware.js`

#### Success Criteria:
- [ ] Redis cache hit rate >75%
- [ ] Database queries reduced by 60%+
- [ ] API response time improved by 70%+
- [ ] CDN serving 90%+ of video traffic
- [ ] Cache invalidation working correctly

---

### Task 4: Code-Level Performance Optimization (20-25 minutes)

**Objective**: Optimize application code for better CPU and memory efficiency.

#### Step 4.1: Parallelize Independent Operations

**Current Problem**:
```javascript
async getVideoPageData(videoId) {
  const video = await getVideo(videoId);           // 50ms
  const comments = await getComments(videoId);     // 100ms
  const related = await getRelated(videoId);       // 150ms
  const user = await getUser(video.userId);        // 30ms
  
  return { video, comments, related, user };
  // Total: 330ms (sequential)
}
```

**Agent Optimization**:
```
These operations are independent. Help me:
1. Execute them in parallel with Promise.all
2. Handle errors gracefully (don't fail entire request)
3. Add timeouts to prevent hanging
4. Consider using Promise.allSettled for resilience
```

**Expected Improvement**: 330ms → 150ms (largest operation)

#### Step 4.2: Optimize Video Recommendation Algorithm

**Current Problem**:
```javascript
async getRecommendations(userId) {
  const allVideos = await getAllVideos();  // 100k videos!
  const userHistory = await getUserHistory(userId);
  
  // O(n²) algorithm!
  const scores = allVideos.map(video => {
    let score = 0;
    for (const hist of userHistory) {
      if (video.tags.some(tag => hist.tags.includes(tag))) {
        score += 1;
      }
    }
    return { video, score };
  });
  
  return scores.sort((a, b) => b.score - a.score).slice(0, 20);
}
```

**Agent Prompt**:
```
This recommendation algorithm is O(n²) and loads 100k videos. Optimize by:
1. Pre-compute recommendations offline (batch job)
2. Use collaborative filtering with matrix factorization
3. Store recommendations in Redis
4. Use approximate nearest neighbors (ANN) for similarity
5. Limit to relevant subset (not all 100k videos)
6. Implement incremental updates
```

**Expected Improvement**: 8000ms → 10ms (pre-computed)

#### Step 4.3: Optimize Data Serialization

**Current Problem**:
```javascript
app.get('/api/videos', async (req, res) => {
  const videos = await Video.findAll({
    include: [User, Comment, Like]  // Loads entire objects
  });
  
  res.json(videos);  // Sends unnecessary data
});
```

**Agent Optimization**:
```
This sends too much data. Help me:
1. Use DTO (Data Transfer Objects) to send only needed fields
2. Implement field filtering (?fields=id,title,thumbnail)
3. Use streaming for large datasets
4. Optimize JSON serialization
5. Consider Protocol Buffers for binary serialization
```

**Expected Improvement**: Response size -70%, serialization time -50%

#### Step 4.4: Implement Connection Pooling

**Current Problem**: Creating new database connections on each request

**Agent Task**:
```
Optimize database connections:
1. Implement proper connection pooling (PostgreSQL, MongoDB)
2. Configure pool size based on load (not too many!)
3. Add connection retry logic
4. Monitor connection usage and leaks
5. Use read replicas for read-heavy operations
```

**Deliverable**: `src/config/database.js` with optimized pooling

#### Success Criteria:
- [ ] Parallel operations implemented where possible
- [ ] Recommendation algorithm optimized
- [ ] Data serialization streamlined
- [ ] Connection pooling configured
- [ ] Code-level improvements measured

---

### Task 5: Load Testing & Benchmarking (15-20 minutes)

**Objective**: Validate optimizations with realistic load tests.

#### Step 5.1: Create Load Testing Scenarios

**Agent-Generated Load Tests**:
```
Create k6 load test scenarios for:
1. User browsing (homepage → video → comments)
2. Search and discovery
3. Video upload
4. Social interactions (like, comment, share)
5. Concurrent streaming (simulate 10k users)

For each scenario:
- Realistic user behavior (think time, flow)
- Ramp-up pattern (gradual load increase)
- Success criteria (error rate <1%, p95 latency)
- Resource monitoring (CPU, memory, DB connections)
```

**Deliverable**: `tests/load/scenarios/`

#### Step 5.2: Run Before/After Benchmarks

```bash
# Baseline (before optimizations)
npm run load:baseline

# After optimizations
npm run load:optimized

# Generate comparison report
npm run load:compare
```

**Metrics to Compare**:
- Requests per second (RPS)
- P50, P95, P99 latencies
- Error rate
- Database query count
- Cache hit rate
- CPU and memory usage
- Cost per 1M requests

**Deliverable**: `reports/PERFORMANCE_COMPARISON.md`

#### Step 5.3: Stress Testing

**Agent Task**:
```
Create stress tests to find breaking point:
1. Gradually increase load until system fails
2. Identify bottleneck causing failure
3. Determine max sustainable throughput
4. Test auto-scaling behavior
5. Test graceful degradation (does system recover?)
```

**Expected**: System handles 50k concurrent users (up from 10k)

#### Success Criteria:
- [ ] Load tests cover main user journeys
- [ ] Before/after comparison documented
- [ ] Performance targets achieved
- [ ] System breaking point identified
- [ ] Auto-scaling validated

---

### Task 6: Monitoring & Observability (10-15 minutes)

**Objective**: Implement performance monitoring for ongoing visibility.

#### Step 6.1: Instrument Application

**Agent Guidance**:
```
Add performance instrumentation:
1. APM integration (New Relic, Datadog, or OpenTelemetry)
2. Custom metrics (request duration, cache hit rate, queue length)
3. Distributed tracing for microservices
4. Real user monitoring (RUM) on frontend
5. Database query tracking
6. Error tracking and alerting
```

**Deliverable**: `src/monitoring/instrumentation.js`

#### Step 6.2: Create Performance Dashboard

**Metrics to Display**:
- API endpoint latencies (p50, p95, p99)
- Database query performance
- Cache hit rates (Redis, CDN)
- Error rates and types
- Throughput (requests/sec)
- Infrastructure costs
- User experience metrics (Apdex score)

**Deliverable**: Grafana dashboard JSON

#### Step 6.3: Set Up Alerts

**Agent-Generated Alerts**:
```
Create alerts for performance degradation:
1. P95 latency >500ms (sustained 5 minutes)
2. Error rate >1%
3. Cache hit rate <70%
4. Database connection pool exhaustion
5. CPU usage >80% (sustained)
6. Disk I/O bottleneck

For each alert:
- Severity level
- Notification channel (Slack, PagerDuty)
- Runbook link
```

**Deliverable**: Alert configurations

#### Success Criteria:
- [ ] APM instrumentation deployed
- [ ] Performance dashboard created
- [ ] Alerts configured and tested
- [ ] Runbooks for common issues
- [ ] Team trained on monitoring tools

---

## 📁 Project Structure

```
04-performance-optimization/
├── README.md                          # This file
├── AGENT_GUIDE.md                     # Performance agent guide
├── SOLUTION_GUIDE.md                  # Complete solutions
├── src/
│   ├── api/
│   │   ├── controllers/
│   │   │   ├── videoController.js     # Video endpoints
│   │   │   ├── feedController.js      # User feed
│   │   │   ├── searchController.js    # Search
│   │   │   └── recommendController.js # Recommendations
│   │   └── middleware/
│   │       ├── cacheMiddleware.js     # Response caching
│   │       └── rateLimitMiddleware.js # Rate limiting
│   ├── services/
│   │   ├── videoService.js            # Business logic
│   │   ├── recommendationService.js   # ML recommendations
│   │   └── transcodeService.js        # Video processing
│   ├── cache/
│   │   ├── videoCache.js              # Redis caching
│   │   ├── feedCache.js               # Feed caching
│   │   └── queryCacheMiddleware.js    # Query result cache
│   ├── models/                        # Database models
│   │   ├── Video.js
│   │   ├── User.js
│   │   ├── Comment.js
│   │   └── View.js
│   ├── config/
│   │   ├── database.js                # DB connection pooling
│   │   ├── redis.js                   # Redis configuration
│   │   └── cdn.js                     # CDN configuration
│   ├── monitoring/
│   │   ├── instrumentation.js         # APM setup
│   │   ├── metrics.js                 # Custom metrics
│   │   └── alerts.js                  # Alert definitions
│   └── utils/
│       ├── asyncHandler.js            # Async utilities
│       └── serialization.js           # Data serialization
├── migrations/
│   ├── add_performance_indexes.sql    # Database indexes
│   └── create_materialized_views.sql  # Aggregation views
├── tests/
│   ├── load/                          # Load tests
│   │   ├── scenarios/
│   │   │   ├── browsing.js
│   │   │   ├── search.js
│   │   │   ├── streaming.js
│   │   │   └── social.js
│   │   └── k6.config.js
│   ├── integration/
│   └── unit/
├── reports/                           # Performance reports
│   ├── BASELINE_PERFORMANCE.md
│   ├── API_PERFORMANCE_ANALYSIS.md
│   ├── DATABASE_ANALYSIS.md
│   ├── CACHING_STRATEGY.md
│   ├── CODE_PERFORMANCE_ISSUES.md
│   ├── PERFORMANCE_COMPARISON.md
│   └── OPTIMIZATION_SUMMARY.md
├── monitoring/
│   ├── grafana-dashboard.json         # Grafana dashboard
│   ├── prometheus.yml                 # Prometheus config
│   └── alerts.yml                     # Alert rules
├── scripts/
│   ├── db-seed.js                     # Seed test data
│   ├── cache-warm.js                  # Pre-warm caches
│   ├── analyze-queries.js             # Query analysis
│   └── benchmark.js                   # Quick benchmarks
└── docker-compose.yml                 # All services
```

---

## 🧪 Performance Testing

### Benchmark Scripts
```bash
# Quick benchmarks
npm run bench:api          # Benchmark API endpoints
npm run bench:db           # Benchmark database queries
npm run bench:cache        # Test cache performance

# Load testing
npm run load:test          # Run load tests
npm run load:stress        # Stress test to failure
npm run load:baseline      # Baseline before optimization
npm run load:optimized     # Test after optimization

# Profiling
npm run profile:cpu        # CPU profiling
npm run profile:memory     # Memory profiling
npm run profile:heap       # Heap snapshot
```

### Database Performance
```bash
# Analyze slow queries
npm run db:slow-queries

# Explain query plans
npm run db:explain

# Check index usage
npm run db:index-stats

# Connection pool stats
npm run db:pool-stats
```

### Cache Performance
```bash
# Redis stats
npm run cache:stats

# Cache hit rate
npm run cache:hit-rate

# Cache warming
npm run cache:warm

# Cache invalidation test
npm run cache:invalidate-test
```

---

## 📊 Success Metrics

### Performance Targets
- ✅ API P95 latency <200ms (from 2000ms+)
- ✅ Page load time <2s (from 8s)
- ✅ Search latency <500ms (from 3000ms)
- ✅ Database query time -70%
- ✅ Cache hit rate >75%
- ✅ Support 50k concurrent users (from 10k)

### Cost Optimization
- ✅ Infrastructure costs -40% ($50k → $30k/month)
- ✅ Database costs -60% (query optimization)
- ✅ CDN costs -50% (better caching)
- ✅ Compute costs -30% (efficiency improvements)

### Throughput & Scalability
- ✅ Requests/second: 3x improvement
- ✅ Videos served/hour: 5x improvement
- ✅ Concurrent users: 5x improvement
- ✅ Error rate <0.5% under load

---

## 📝 Submission Requirements

### 1. Performance Analysis (Required)
- `reports/BASELINE_PERFORMANCE.md` - Current state
- `reports/API_PERFORMANCE_ANALYSIS.md` - API bottlenecks
- `reports/DATABASE_ANALYSIS.md` - Database optimization
- `reports/CACHING_STRATEGY.md` - Caching design
- `reports/PERFORMANCE_COMPARISON.md` - Before/after metrics
- `reports/OPTIMIZATION_SUMMARY.md` - Executive summary

### 2. Optimized Code
- Database query optimizations
- Caching implementations
- Code-level improvements
- Migrations for indexes and schema changes

### 3. Testing Evidence
- Load test results (before/after)
- Benchmark comparisons
- Cache hit rate metrics
- Database query performance metrics

### 4. Monitoring Setup
- APM instrumentation
- Grafana dashboard
- Alert configurations
- Performance runbooks

### 5. Reflection
Create `PERFORMANCE_LESSONS.md` covering:
- How agents helped identify bottlenecks
- Most impactful optimizations
- Trade-offs made (complexity vs performance)
- Lessons learned about performance engineering
- Best practices for AI-assisted optimization

---

## 🏆 Bonus Challenges

### Advanced Optimizations
- [ ] Implement GraphQL with DataLoader (batch/cache)
- [ ] Add edge caching with Cloudflare Workers
- [ ] Implement database sharding for horizontal scaling
- [ ] Add request coalescing for duplicate requests
- [ ] Implement adaptive cache TTLs based on access patterns

### Infrastructure
- [ ] Set up auto-scaling based on performance metrics
- [ ] Implement blue-green deployment for zero downtime
- [ ] Add chaos engineering tests (latency injection)
- [ ] Set up multi-region deployment for global performance
- [ ] Implement connection pooling with PgBouncer

### Advanced Monitoring
- [ ] Real user monitoring (RUM) on frontend
- [ ] Synthetic monitoring for proactive alerts
- [ ] Cost attribution per feature/endpoint
- [ ] Performance budget enforcement in CI/CD
- [ ] Anomaly detection with machine learning

---

## 💡 Tips for Success

### Performance Analysis with Agents
1. **Data-Driven**: Always measure before optimizing
2. **Systematic**: Profile each layer (API, database, cache, code)
3. **Prioritize**: Focus on highest-impact bottlenecks first
4. **Validate**: Benchmark every optimization
5. **Monitor**: Watch for regressions in production

### Effective Performance Prompts
- "Analyze this query's EXPLAIN plan and suggest indexes"
- "What's the time complexity of this algorithm? Can we do better?"
- "Design a caching strategy for this data with 10:1 read/write ratio"
- "Help me parallelize these independent operations"
- "What's causing high memory usage in this function?"

### Optimization Strategy
1. **Low-Hanging Fruit**: Start with easy wins (indexes, caching)
2. **Measure Everything**: Instrument before and after
3. **Trade-offs**: Understand complexity vs performance
4. **Don't Over-Optimize**: Stop when targets are met
5. **Monitor in Production**: Dev performance ≠ production

---

## 🔗 Resources

### Performance Best Practices
- [Web Performance](https://web.dev/performance/)
- [Node.js Performance](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Database Performance Tuning](https://use-the-index-luke.com/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

### Tools
- [k6 Load Testing](https://k6.io/)
- [Clinic.js Node.js Performance](https://clinicjs.org/)
- [New Relic APM](https://newrelic.com/)
- [Grafana Dashboards](https://grafana.com/)

### Optimization Techniques
- [Caching Strategies](https://aws.amazon.com/caching/)
- [Database Indexing](https://www.postgresql.org/docs/current/indexes.html)
- [CDN Best Practices](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/)

---

## 🎓 Learning Outcomes

After completing this challenge, you'll be able to:

- ✅ Profile applications to identify performance bottlenecks
- ✅ Optimize database queries with indexes and query tuning
- ✅ Design and implement multi-layer caching strategies
- ✅ Improve code-level performance (algorithms, parallelization)
- ✅ Conduct realistic load testing and benchmarking
- ✅ Set up performance monitoring and alerting
- ✅ Make data-driven optimization decisions with AI assistance
- ✅ Balance performance, cost, and complexity trade-offs

---

**Ready to supercharge the streaming platform? Deploy your performance engineering agents and optimize for speed and efficiency!** ⚡🚀

**[⬅️ Back to Challenges](../)** | **[🏠 Main Workshop](../../README.md)**
