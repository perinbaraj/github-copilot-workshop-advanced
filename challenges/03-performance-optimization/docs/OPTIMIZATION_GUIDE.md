# Performance Optimization Guide

## 📊 Optimization Phases

### Phase 1: Database Indexing (Quick Win)
**Time:** 30 minutes  
**Expected Improvement:** 50% faster queries

1. **Apply database indexes:**
   ```bash
   # Connect to PostgreSQL
   docker exec -it 03-performance-optimization-postgres-1 psql -U admin -d streamvibe
   
   # Run migration
   \i /path/to/scripts/add_indexes.sql
   ```

2. **Verify index creation:**
   ```sql
   SELECT tablename, indexname 
   FROM pg_indexes 
   WHERE schemaname = 'public'
   ORDER BY tablename;
   ```

3. **Test query performance:**
   ```sql
   EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;
   -- Should show "Index Scan" instead of "Seq Scan"
   ```

---

### Phase 2: Fix N+1 Queries
**Time:** 45 minutes  
**Expected Improvement:** 80% faster API responses

#### Fix 1: Video Details Endpoint

**Before (5 queries):**
```javascript
const video = await pgPool.query('SELECT * FROM videos WHERE id = $1', [id]);
const user = await pgPool.query('SELECT * FROM users WHERE id = $1', [video.user_id]);
const likes = await pgPool.query('SELECT COUNT(*) FROM likes WHERE video_id = $1', [id]);
// ... 2 more queries
```

**After (1 query with JOINs):**
```javascript
const result = await pgPool.query(`
  SELECT 
    v.*,
    u.id as user_id, u.username, u.avatar,
    COUNT(DISTINCT l.id) as like_count,
    COUNT(DISTINCT c.id) as comment_count,
    COUNT(DISTINCT vw.id) as view_count
  FROM videos v
  LEFT JOIN users u ON v.user_id = u.id
  LEFT JOIN likes l ON v.id = l.video_id
  LEFT JOIN comments c ON v.id = c.video_id
  LEFT JOIN views vw ON v.id = vw.video_id
  WHERE v.id = $1
  GROUP BY v.id, u.id
`, [id]);

const video = result.rows[0];
```

#### Fix 2: Video List Endpoint

**Before (N+1 queries):**
```javascript
const videos = await pgPool.query('SELECT * FROM videos');
for (const video of videos.rows) {
  const user = await pgPool.query('SELECT username FROM users WHERE id = $1', [video.user_id]);
  video.username = user.rows[0].username;
}
```

**After (1 query with JOIN and pagination):**
```javascript
const page = parseInt(req.query.page) || 1;
const limit = parseInt(req.query.limit) || 20;
const offset = (page - 1) * limit;

const result = await pgPool.query(`
  SELECT 
    v.*,
    u.username, u.avatar,
    COUNT(l.id) as like_count,
    COUNT(vw.id) as view_count
  FROM videos v
  LEFT JOIN users u ON v.user_id = u.id
  LEFT JOIN likes l ON v.id = l.video_id
  LEFT JOIN views vw ON v.id = vw.video_id
  GROUP BY v.id, u.id
  ORDER BY v.created_at DESC
  LIMIT $1 OFFSET $2
`, [limit, offset]);
```

---

### Phase 3: Implement Redis Caching
**Time:** 45 minutes  
**Expected Improvement:** 70% cache hit rate

#### Setup Redis Connection

```javascript
const redis = require('redis');
const { promisify } = require('util');

const redisClient = redis.createClient({
  host: 'localhost',
  port: 6379
});

redisClient.on('error', (err) => console.log('Redis Error:', err));

const getAsync = promisify(redisClient.get).bind(redisClient);
const setexAsync = promisify(redisClient.setex).bind(redisClient);
const delAsync = promisify(redisClient.del).bind(redisClient);
```

#### Cache Wrapper Function

```javascript
async function cacheWrapper(key, ttl, fetchFunction) {
  // Try to get from cache
  const cached = await getAsync(key);
  if (cached) {
    console.log(`Cache HIT: ${key}`);
    return JSON.parse(cached);
  }
  
  // Cache miss - fetch from database
  console.log(`Cache MISS: ${key}`);
  const data = await fetchFunction();
  
  // Store in cache
  await setexAsync(key, ttl, JSON.stringify(data));
  
  return data;
}
```

#### Apply Caching to Video Details

```javascript
app.get('/api/videos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const cacheKey = `video:${id}`;
    
    const video = await cacheWrapper(cacheKey, 300, async () => {
      const result = await pgPool.query(`
        SELECT v.*, u.username, u.avatar,
          COUNT(DISTINCT l.id) as like_count,
          COUNT(DISTINCT c.id) as comment_count,
          COUNT(DISTINCT vw.id) as view_count
        FROM videos v
        LEFT JOIN users u ON v.user_id = u.id
        LEFT JOIN likes l ON v.id = l.video_id
        LEFT JOIN comments c ON v.id = c.video_id
        LEFT JOIN views vw ON v.id = vw.video_id
        WHERE v.id = $1
        GROUP BY v.id, u.id
      `, [id]);
      
      return result.rows[0];
    });
    
    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    res.json(video);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

#### Cache Invalidation

```javascript
// When video is updated
app.put('/api/videos/:id', async (req, res) => {
  const { id } = req.params;
  
  // Update database
  await pgPool.query('UPDATE videos SET ... WHERE id = $1', [id]);
  
  // Invalidate cache
  await delAsync(`video:${id}`);
  
  res.json({ success: true });
});
```

#### Caching Strategy

| Data Type | TTL | Key Pattern | Invalidation |
|-----------|-----|-------------|--------------|
| Video details | 5 min | `video:{id}` | On update/delete |
| Video list | 1 min | `videos:page:{n}` | On new upload |
| Search results | 10 min | `search:{query}` | None (expire) |
| User profile | 5 min | `user:{id}` | On update |
| Recommendations | 30 min | `recs:{userId}` | On new watch |

---

### Phase 4: Optimize Search
**Time:** 30 minutes  
**Expected Improvement:** 30x faster searches

#### Before (LIKE - very slow)

```javascript
const result = await pgPool.query(`
  SELECT * FROM videos 
  WHERE title LIKE $1 OR description LIKE $1
`, [`%${query}%`]);
```

#### After (Full-text search)

```javascript
app.get('/api/search', async (req, res) => {
  try {
    const { q } = req.query;
    const cacheKey = `search:${q}`;
    
    const results = await cacheWrapper(cacheKey, 600, async () => {
      const result = await pgPool.query(`
        SELECT 
          v.*,
          u.username,
          ts_rank(v.search_vector, query) as rank
        FROM videos v
        LEFT JOIN users u ON v.user_id = u.id,
        plainto_tsquery('english', $1) query
        WHERE v.search_vector @@ query
        ORDER BY rank DESC
        LIMIT 50
      `, [q]);
      
      return result.rows;
    });
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

### Phase 5: Optimize Recommendation Algorithm
**Time:** 60 minutes  
**Expected Improvement:** 30x faster (15s → 500ms)

#### Before (O(n²) - extremely slow)

```javascript
// Loads ALL videos into memory
const allVideos = await pgPool.query('SELECT * FROM videos');

// Nested loops - O(n²)
for (const video of allVideos.rows) {
  for (const watchedId of watchedIds) {
    const similarity = await pgPool.query(/* ... */);
    score += similarity;
  }
}
```

#### After (Database-powered - O(n log n))

```javascript
app.get('/api/recommendations/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const cacheKey = `recommendations:${userId}`;
    
    const recommendations = await cacheWrapper(cacheKey, 1800, async () => {
      const result = await pgPool.query(`
        WITH user_tags AS (
          -- Get tags from videos user has watched
          SELECT DISTINCT vt.tag
          FROM views v
          JOIN video_tags vt ON v.video_id = vt.video_id
          WHERE v.user_id = $1
        ),
        video_scores AS (
          -- Calculate similarity score for unwatched videos
          SELECT 
            v.id,
            v.title,
            v.thumbnail_url,
            COUNT(DISTINCT vt.tag) as similarity_score,
            v.created_at
          FROM videos v
          JOIN video_tags vt ON v.id = vt.video_id
          WHERE vt.tag IN (SELECT tag FROM user_tags)
            AND v.id NOT IN (
              SELECT video_id FROM views WHERE user_id = $1
            )
          GROUP BY v.id
          HAVING COUNT(DISTINCT vt.tag) >= 2
        )
        SELECT 
          vs.*,
          u.username,
          COUNT(l.id) as like_count
        FROM video_scores vs
        JOIN videos v ON vs.id = v.id
        JOIN users u ON v.user_id = u.id
        LEFT JOIN likes l ON v.id = l.video_id
        GROUP BY vs.id, vs.title, vs.thumbnail_url, vs.similarity_score, vs.created_at, u.username
        ORDER BY vs.similarity_score DESC, vs.created_at DESC
        LIMIT 20
      `, [userId]);
      
      return result.rows;
    });
    
    res.json(recommendations);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

### Phase 6: Parallelize Sequential Operations
**Time:** 15 minutes  
**Expected Improvement:** 4x faster

#### Before (Sequential - 1200ms)

```javascript
const video = await getVideo(id);
const comments = await getComments(id);
const related = await getRelatedVideos(id);
const user = await getUser(video.user_id);
```

#### After (Parallel - 300ms)

```javascript
const [video, comments, related] = await Promise.all([
  getVideo(id),
  getComments(id),
  getRelatedVideos(id)
]);

const user = await getUser(video.user_id);  // Depends on video result
```

---

### Phase 7: Configure Connection Pooling
**Time:** 15 minutes  
**Expected Improvement:** Better resource utilization

```javascript
const { Pool } = require('pg');

const pgPool = new Pool({
  host: 'localhost',
  database: 'streamvibe',
  user: 'admin',
  password: 'admin123',
  // Optimization settings
  max: 20,                      // Maximum pool size
  min: 5,                       // Minimum pool size
  idleTimeoutMillis: 30000,     // Close idle clients after 30s
  connectionTimeoutMillis: 2000, // Timeout if pool is full
});

// Handle pool errors
pgPool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pgPool.end();
  console.log('Pool closed');
});
```

---

## 📊 Testing Performance Improvements

### 1. Benchmark Response Times

```bash
# Install Apache Bench
# sudo apt-get install apache2-utils  # Linux
# brew install httpd  # macOS

# Test video details endpoint
ab -n 1000 -c 10 http://localhost:3000/api/videos/1

# Look for:
# - Time per request
# - Requests per second
# - Connection Times (mean, median)
```

### 2. Monitor Cache Hit Rate

```bash
# Redis CLI
redis-cli
> INFO stats

# Look for:
# - keyspace_hits
# - keyspace_misses
# - Hit rate = hits / (hits + misses)
```

### 3. Database Query Performance

```sql
-- Enable timing
\timing on

-- Test query performance
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;

-- Check for:
-- - "Index Scan" (good) vs "Seq Scan" (bad)
-- - Execution time
-- - Rows returned
```

### 4. Load Testing

```bash
# Install autocannon
npm install -g autocannon

# Test endpoint under load
autocannon -c 100 -d 30 http://localhost:3000/api/videos/1

# Parameters:
# -c: concurrent connections
# -d: duration in seconds
```

---

## 🎯 Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Video Details API | 1200ms | 50ms | 24x faster |
| Video List API | 8000ms | 200ms | 40x faster |
| Search API | 3000ms | 100ms | 30x faster |
| Recommendations | 15000ms | 500ms | 30x faster |
| Cache Hit Rate | 0% | 70% | ∞ |
| Database Load | 100% | 30% | 70% reduction |
| Concurrent Users | 10 | 100+ | 10x capacity |

---

## 🐛 Common Issues

### Issue: Cache not working
**Solution:** Make sure Redis is running
```bash
docker-compose ps  # Check if redis is up
docker-compose logs redis  # Check logs
```

### Issue: Indexes not being used
**Solution:** Run ANALYZE to update statistics
```sql
ANALYZE videos;
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;
-- Should show "Index Scan using idx_videos_user_id"
```

### Issue: Out of database connections
**Solution:** Increase pool size or fix connection leaks
```javascript
// Always release connections
const client = await pool.connect();
try {
  const result = await client.query('...');
} finally {
  client.release();  // Important!
}
```

---

## ✅ Verification Checklist

- [ ] All indexes created successfully
- [ ] N+1 queries eliminated (1 query per endpoint)
- [ ] Redis caching implemented with 70%+ hit rate
- [ ] Full-text search working
- [ ] Recommendations respond in <500ms
- [ ] Pagination implemented for list endpoints
- [ ] Parallel operations used where possible
- [ ] Connection pool configured
- [ ] Load testing shows 10x improvement
- [ ] Documentation updated
