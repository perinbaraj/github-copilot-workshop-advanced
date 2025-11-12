# Performance Issues Documentation

## 🔴 Critical Performance Bottlenecks

### 1. N+1 Query Problems

#### Issue 1.1: Video Details Endpoint
**Location:** `src/server.js:26-57`
**Severity:** 🔴 Critical
**Impact:** 5+ database queries per video request

```javascript
// Current Implementation (BAD)
app.get('/api/videos/:id', async (req, res) => {
  const video = await pgPool.query('SELECT * FROM videos WHERE id = $1', [id]);
  const user = await pgPool.query('SELECT * FROM users WHERE id = $1', [video.user_id]);
  const likes = await pgPool.query('SELECT COUNT(*) FROM likes WHERE video_id = $1', [id]);
  const comments = await pgPool.query('SELECT COUNT(*) FROM comments WHERE video_id = $1', [id]);
  const views = await pgPool.query('SELECT COUNT(*) FROM views WHERE video_id = $1', [id]);
});
```

**Recommended Solution:**
```sql
-- Use a single JOIN query
SELECT 
  v.*,
  u.username, u.avatar,
  COUNT(DISTINCT l.id) as like_count,
  COUNT(DISTINCT c.id) as comment_count,
  COUNT(DISTINCT vw.id) as view_count
FROM videos v
LEFT JOIN users u ON v.user_id = u.id
LEFT JOIN likes l ON v.id = l.video_id
LEFT JOIN comments c ON v.id = c.video_id
LEFT JOIN views vw ON v.id = vw.video_id
WHERE v.id = $1
GROUP BY v.id, u.id;
```

**Expected Improvement:** 5 queries → 1 query (80% faster)

---

#### Issue 1.2: Video List Endpoint
**Location:** `src/server.js:60-78`
**Severity:** 🔴 Critical
**Impact:** N+1 queries for each video (100k+ queries for all videos)

```javascript
// Current Implementation (BAD)
app.get('/api/videos', async (req, res) => {
  const result = await pgPool.query('SELECT * FROM videos');
  for (const video of result.rows) {
    const user = await pgPool.query('SELECT username FROM users WHERE id = $1', [video.user_id]);
    video.username = user.rows[0].username;
  }
});
```

**Recommended Solution:**
```sql
-- Use JOIN and pagination
SELECT v.*, u.username, u.avatar
FROM videos v
LEFT JOIN users u ON v.user_id = u.id
ORDER BY v.created_at DESC
LIMIT 20 OFFSET 0;
```

**Expected Improvement:** 100k+ queries → 1 query (99% faster)

---

### 2. Missing Database Indexes

#### Index 2.1: videos(user_id)
**Impact:** Full table scan on user video queries
**Queries Affected:** User profile pages, user feed
**Size Impact:** ~5MB for 1M records

```sql
CREATE INDEX idx_videos_user_id ON videos(user_id);
```

---

#### Index 2.2: videos(created_at)
**Impact:** Slow sorting on timeline queries
**Queries Affected:** Video list, feeds

```sql
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);
```

---

#### Index 2.3: views(video_id, user_id)
**Impact:** Duplicate view checks are slow
**Queries Affected:** View recording, analytics

```sql
CREATE INDEX idx_views_video_user ON views(video_id, user_id);
```

---

#### Index 2.4: comments(video_id, created_at)
**Impact:** Comment loading is slow
**Queries Affected:** Comment sections

```sql
CREATE INDEX idx_comments_video_created ON comments(video_id, created_at DESC);
```

---

#### Index 2.5: likes(video_id)
**Impact:** Like count aggregations are slow

```sql
CREATE INDEX idx_likes_video_id ON likes(video_id);
```

---

#### Index 2.6: video_tags(tag)
**Impact:** Tag-based search is slow

```sql
CREATE INDEX idx_video_tags_tag ON video_tags(tag);
```

---

#### Index 2.7: Full-Text Search Index
**Impact:** Search uses LIKE which is very slow

```sql
-- Add tsvector column
ALTER TABLE videos ADD COLUMN search_vector tsvector;

-- Create GIN index for full-text search
CREATE INDEX idx_videos_search ON videos USING GIN(search_vector);

-- Create trigger to update search vector
CREATE TRIGGER videos_search_vector_update
BEFORE INSERT OR UPDATE ON videos
FOR EACH ROW EXECUTE FUNCTION
  tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
```

---

### 3. Inefficient Algorithms

#### Algorithm 3.1: Recommendation Engine
**Location:** `src/server.js:96-126`
**Severity:** 🔴 Critical
**Time Complexity:** O(n²) where n = 100k videos
**Impact:** 15+ second response time

```javascript
// Current Implementation (BAD)
for (const video of allVideos) {  // O(n)
  for (const watchedId of watchedIds) {  // O(m)
    const similarity = await pgPool.query(/* ... */);  // N+1 queries!
    score += similarity;
  }
}
```

**Recommended Solution:**
```sql
-- Use database for heavy lifting
WITH user_tags AS (
  SELECT DISTINCT vt.tag
  FROM views v
  JOIN video_tags vt ON v.video_id = vt.video_id
  WHERE v.user_id = $1
),
video_scores AS (
  SELECT 
    v.id,
    COUNT(DISTINCT vt.tag) as similarity_score
  FROM videos v
  JOIN video_tags vt ON v.id = vt.video_id
  WHERE vt.tag IN (SELECT tag FROM user_tags)
    AND v.id NOT IN (SELECT video_id FROM views WHERE user_id = $1)
  GROUP BY v.id
)
SELECT v.*, vs.similarity_score
FROM videos v
JOIN video_scores vs ON v.id = vs.id
ORDER BY vs.similarity_score DESC, v.created_at DESC
LIMIT 20;
```

**Expected Improvement:** O(n²) → O(n log n), 15s → <500ms (30x faster)

---

### 4. No Caching Implementation

#### Cache 4.1: Video Details
**Impact:** Every request hits database
**Solution:** Cache for 5 minutes

```javascript
const cacheKey = `video:${id}`;
const cached = await redisClient.get(cacheKey);
if (cached) return JSON.parse(cached);

// Fetch from database
const video = await getVideoFromDB(id);
await redisClient.setex(cacheKey, 300, JSON.stringify(video));
```

**Expected Cache Hit Rate:** 70-80%

---

#### Cache 4.2: Search Results
**Impact:** Complex search queries repeat
**Solution:** Cache for 10 minutes

```javascript
const cacheKey = `search:${query}`;
// Cache implementation
```

---

#### Cache 4.3: User Feed
**Impact:** Timeline generation is expensive
**Solution:** Cache for 1 minute

```javascript
const cacheKey = `feed:${userId}`;
// Cache implementation with shorter TTL
```

---

### 5. No Pagination

#### Issue 5.1: Video List Returns All Records
**Impact:** Transfers 100k+ records (50MB+) per request
**Solution:** Add pagination

```javascript
const page = parseInt(req.query.page) || 1;
const limit = parseInt(req.query.limit) || 20;
const offset = (page - 1) * limit;

const result = await pgPool.query(
  'SELECT * FROM videos ORDER BY created_at DESC LIMIT $1 OFFSET $2',
  [limit, offset]
);
```

---

### 6. Sequential Operations

#### Issue 6.1: Video Page Loads Data Sequentially
**Location:** `src/server.js:129-141`
**Impact:** 4 sequential queries (1200ms) instead of parallel (300ms)

```javascript
// Current (BAD)
const video = await getVideo(id);
const comments = await getComments(id);
const related = await getRelatedVideos(id);
const user = await getUser(video.user_id);

// Recommended (GOOD)
const [video, comments, related, user] = await Promise.all([
  getVideo(id),
  getComments(id),
  getRelatedVideos(id),
  getUser(video.user_id)
]);
```

**Expected Improvement:** 4x faster (1200ms → 300ms)

---

### 7. Connection Pool Issues

#### Issue 7.1: No Pool Configuration
**Impact:** Default pool size (10) is too small for load

```javascript
// Recommended Configuration
const pgPool = new Pool({
  host: 'localhost',
  database: 'streamvibe',
  user: 'admin',
  password: 'admin123',
  max: 20,  // Maximum pool size
  min: 5,   // Minimum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

---

#### Issue 7.2: MongoDB Connection Per Request
**Impact:** Creates new connection for each request

```javascript
// Current (BAD)
const mongoClient = new MongoClient(mongoUri);
await mongoClient.connect();  // Every request!

// Recommended (GOOD)
let mongoClient;
let db;

async function connectMongo() {
  if (!mongoClient) {
    mongoClient = new MongoClient(mongoUri, { maxPoolSize: 10 });
    await mongoClient.connect();
    db = mongoClient.db('streamvibe');
  }
  return db;
}
```

---

## 📊 Performance Impact Summary

| Issue | Current | Target | Impact |
|-------|---------|--------|--------|
| Video details N+1 | 1200ms | 50ms | 24x faster |
| Video list N+1 | 8000ms | 200ms | 40x faster |
| Search LIKE | 3000ms | 100ms | 30x faster |
| Recommendations O(n²) | 15000ms | 500ms | 30x faster |
| Missing indexes | Full scans | Index scans | 10-100x faster |
| No caching | 100% DB load | 70% cache hit | 3x faster |
| No pagination | 50MB transfer | 100KB transfer | 99% reduction |
| Sequential ops | 1200ms | 300ms | 4x faster |

---

## 🛠️ Implementation Priority

### Phase 1: Quick Wins (1-2 hours)
1. Add missing database indexes
2. Implement pagination
3. Parallelize sequential operations

**Expected Impact:** 50% improvement

### Phase 2: Major Optimizations (2-3 hours)
1. Fix all N+1 queries with JOINs
2. Implement Redis caching
3. Refactor recommendation algorithm

**Expected Impact:** 90% improvement

### Phase 3: Advanced (2-3 hours)
1. Implement full-text search
2. Connection pool tuning
3. Query optimization with EXPLAIN
4. Monitoring and profiling

**Expected Impact:** 95%+ improvement

---

## 🧪 Testing Each Fix

Use these queries to verify improvements:

```sql
-- Before optimization
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;

-- After adding index
CREATE INDEX idx_videos_user_id ON videos(user_id);
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;
-- Should show "Index Scan" instead of "Seq Scan"
```

---

## 📈 Monitoring Queries

```sql
-- Check index usage
SELECT 
  schemaname, tablename, indexname, 
  idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check cache hit ratio
SELECT 
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```
