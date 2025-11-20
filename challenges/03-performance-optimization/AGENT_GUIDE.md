# Agent Guide: Performance Optimization Challenge

## 🎯 Challenge Overview

You are a **Performance Engineering Agent** tasked with identifying and fixing critical performance bottlenecks in the StreamVibe video streaming platform. The application is experiencing severe performance issues that impact user experience and operational costs.

## 📊 Current State

### Application Architecture
- **Backend:** Node.js/Express API
- **Database:** PostgreSQL (relational data)
- **Cache:** Redis (not currently utilized)
- **Data:** 100k+ videos, 1M+ users, 10M+ views

### Known Issues
1. **Critical:** N+1 query problems causing 5-10 second response times
2. **Critical:** No database indexes (full table scans)
3. **High:** No caching implementation
4. **High:** O(n²) recommendation algorithm
5. **High:** No pagination (returns all 100k videos)
6. **Medium:** Sequential operations that could be parallel
7. **Medium:** No connection pooling optimization

## 🤖 Agent Capabilities You'll Use

### 1. Performance Profiler Agent
**Skills:**
- Identify N+1 query patterns
- Find missing database indexes
- Detect inefficient algorithms
- Spot memory leaks
- Analyze query execution plans

**Example Prompts:**
```
@workspace Analyze the codebase for N+1 query problems. 
Show me specific examples with line numbers.

@workspace Check which database tables are missing indexes. 
Review the queries in server.js and identify slow operations.

@workspace Find all O(n²) or worse algorithmic complexity issues.
```

### 2. Database Architect Agent
**Skills:**
- Design optimal indexes
- Rewrite queries with JOINs
- Implement query optimization
- Add pagination
- Design efficient schemas

**Example Prompts:**
```
@workspace Review the video details endpoint. How can we reduce 
the 5 database queries to a single optimized query with JOINs?

@workspace Design indexes for the videos, views, and comments tables. 
Consider the query patterns in server.js.

@workspace Add pagination to the video list endpoint with proper 
limit/offset handling.
```

### 3. Caching Expert Agent
**Skills:**
- Design multi-layer caching strategies
- Implement Redis caching
- Set appropriate TTLs
- Handle cache invalidation
- Batch operations

**Example Prompts:**
```
@workspace Implement Redis caching for the video details endpoint. 
Use appropriate TTL and cache key strategies.

@workspace Design a caching strategy for the recommendations endpoint. 
Consider cache warming and invalidation.

@workspace Implement view count batching with Redis to reduce 
database writes.
```

### 4. Code Optimization Agent
**Skills:**
- Refactor inefficient algorithms
- Implement parallel operations
- Optimize loops and iterations
- Reduce computational complexity
- Apply async patterns

**Example Prompts:**
```
@workspace The recommendations endpoint has an O(n²) algorithm. 
Refactor it to O(n log n) or better.

@workspace The video page endpoint makes 4 sequential queries. 
Refactor to use Promise.all for parallel execution.

@workspace Optimize the search implementation to use PostgreSQL 
full-text search instead of LIKE queries.
```

## 📋 Step-by-Step Approach

### Phase 1: Assessment (15 minutes)
**Goal:** Understand current performance issues

**Agent Prompts:**
1. "Analyze the codebase for performance bottlenecks"
2. "List all database queries and identify inefficient ones"
3. "Check for missing indexes on frequently queried columns"
4. "Identify endpoints with the highest response times"

**Expected Output:**
- List of N+1 query locations
- Missing index recommendations
- Slow endpoint identification
- Algorithmic complexity analysis

### Phase 2: Database Optimization (30 minutes)
**Goal:** Fix queries and add indexes

**Agent Prompts:**
```
@workspace Fix the N+1 query problem in /api/videos/:id. 
Combine the 5 separate queries into one JOIN query.

@workspace Add database indexes for:
- videos(user_id)
- videos(created_at)
- views(video_id, user_id)
- comments(video_id)
Review add_indexes.sql and verify completeness.

@workspace Add pagination to /api/videos endpoint. 
Implement page and limit query parameters with proper SQL.
```

**Expected Changes:**
- Single JOIN query for video details (5 queries → 1)
- Indexes added to frequently queried columns
- Pagination implemented (default 20 items per page)
- Query response time < 100ms

### Phase 3: Caching Implementation (30 minutes)
**Goal:** Implement Redis caching

**Agent Prompts:**
```
@workspace Implement caching for the video details endpoint using Redis. 
Cache key should be 'video:{id}' with 1 hour TTL.

@workspace Create a cache layer for trending videos with 5-minute TTL. 
Implement cache warming on startup.

@workspace Implement view count batching: 
- Increment counts in Redis
- Batch write to database every 5 minutes
- Use sorted sets for efficient aggregation
```

**Expected Changes:**
- Video details cached (cache hit rate > 80%)
- Trending videos cached
- View counts batched (10x fewer DB writes)
- Cache invalidation on updates

### Phase 4: Algorithm Optimization (45 minutes)
**Goal:** Fix O(n²) recommendation algorithm

**Agent Prompts:**
```
@workspace The recommendations endpoint loads all 100k videos and 
has O(n²) complexity. Redesign using:
1. Precomputed similarity scores
2. Database-side filtering
3. Limit to top 100 candidates
4. Cache results per user

@workspace Implement collaborative filtering using:
- User-video interaction matrix
- Cosine similarity (pre-computed)
- K-nearest neighbors approach
Target: < 500ms response time
```

**Expected Changes:**
- Algorithm complexity O(n log n) or better
- Database-side filtering
- Pre-computed similarity scores
- Cached recommendations
- Response time < 500ms

### Phase 5: Concurrent Operations (20 minutes)
**Goal:** Parallelize independent queries

**Agent Prompts:**
```
@workspace The /api/videos/:id/page endpoint makes 4 sequential 
queries that are independent. Refactor to use Promise.all() for 
parallel execution.

@workspace Identify other endpoints with sequential operations 
that could be parallelized.
```

**Expected Changes:**
- Video page load time reduced by 50%
- All independent queries parallelized

### Phase 6: Load Testing (20 minutes)
**Goal:** Validate improvements

**Agent Prompts:**
```
@workspace Review the k6 load test scripts in tests/load/scenarios/. 
Update thresholds based on our optimizations.

@workspace Generate a load test that simulates 100 concurrent users 
browsing videos, with 95th percentile response time < 500ms.
```

**Testing Commands:**
```bash
# Run benchmark
npm run test:perf

# Run k6 load tests
k6 run tests/load/scenarios/browsing.js
k6 run tests/load/scenarios/search.js
k6 run tests/load/scenarios/streaming.js

# Check results
# - P95 response time < 500ms
# - Error rate < 1%
# - Throughput > 100 req/sec
```

## 🎯 Success Criteria

### Performance Targets

| Metric | Before | Target | Stretch Goal |
|--------|--------|--------|--------------|
| Video Details (P95) | 5000ms | <500ms | <200ms |
| Video List (P95) | 10000ms | <300ms | <100ms |
| Search (P95) | 8000ms | <1000ms | <500ms |
| Recommendations (P95) | 15000ms | <2000ms | <500ms |
| Error Rate | 5% | <1% | <0.1% |
| Throughput | 10 req/s | >100 req/s | >500 req/s |

### Database Optimization
- ✅ All N+1 queries eliminated
- ✅ Indexes on all foreign keys
- ✅ Composite indexes for common queries
- ✅ Pagination on all list endpoints
- ✅ Query execution time < 50ms

### Caching
- ✅ Redis connected and configured
- ✅ Video details cached (>80% hit rate)
- ✅ Trending videos cached
- ✅ User feeds cached
- ✅ Recommendations cached
- ✅ Cache invalidation working

### Code Quality
- ✅ No O(n²) algorithms
- ✅ Parallel execution where possible
- ✅ Connection pooling optimized
- ✅ Error handling improved
- ✅ Logging for performance monitoring

## 🚨 Common Pitfalls to Avoid

### ❌ Don't Do This:
1. **Over-caching:** Caching data that changes frequently
2. **Cache without invalidation:** Serving stale data
3. **Premature optimization:** Optimizing before measuring
4. **Ignoring N+1 queries:** Trying to cache around bad queries
5. **No pagination:** Loading all records even with indexes

### ✅ Do This Instead:
1. **Measure first:** Use benchmarks to identify bottlenecks
2. **Fix queries first:** Optimize database queries before caching
3. **Cache wisely:** Cache expensive operations with appropriate TTL
4. **Paginate everything:** Never load all records
5. **Monitor continuously:** Add logging and metrics

## 📊 Monitoring & Validation

### Check Query Performance
```sql
-- Enable query timing
\timing

-- Explain query plan
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;

-- Check index usage
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('videos', 'views', 'comments', 'likes');
```

### Check Cache Hit Rates
```javascript
// Add to each cached endpoint
const cacheHits = await redis.get('cache:hits');
const cacheMisses = await redis.get('cache:misses');
const hitRate = cacheHits / (cacheHits + cacheMisses);
console.log(`Cache hit rate: ${(hitRate * 100).toFixed(2)}%`);
```

### Load Testing Validation
```bash
# Before optimization
k6 run tests/load/scenarios/browsing.js
# Expected: Many failures, P95 > 5000ms

# After optimization
k6 run tests/load/scenarios/browsing.js
# Expected: <1% failures, P95 < 500ms
```

## 🎓 Learning Outcomes

After completing this challenge, you will be able to:
1. ✅ Identify and fix N+1 query problems
2. ✅ Design and implement database indexes
3. ✅ Implement effective caching strategies
4. ✅ Optimize algorithmic complexity
5. ✅ Use parallel execution patterns
6. ✅ Conduct load testing and performance profiling
7. ✅ Use GitHub Copilot agents for performance engineering

## 🔗 Related Resources

- [CURRENT_ISSUES.md](./CURRENT_ISSUES.md) - Detailed issue list
- [OPTIMIZATION_GUIDE.md](./OPTIMIZATION_GUIDE.md) - Optimization techniques
- [PostgreSQL Index Documentation](https://www.postgresql.org/docs/current/indexes.html)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
- [k6 Load Testing Guide](https://k6.io/docs/)

---

**Remember:** Performance optimization is an iterative process. Measure, optimize, validate, repeat!
