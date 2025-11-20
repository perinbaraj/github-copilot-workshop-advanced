# Solution Guide: Performance Optimization Challenge

## 🎯 Overview

This guide provides complete solutions for all performance issues in the StreamVibe platform. Use this as a reference after attempting the challenge yourself.

## 📊 Performance Improvements Summary

| Optimization | Impact | Difficulty | Time |
|--------------|--------|------------|------|
| Database Indexes | 90% faster queries | Easy | 15 min |
| Fix N+1 Queries | 80% faster endpoints | Medium | 30 min |
| Add Pagination | 95% less data transfer | Easy | 15 min |
| Implement Caching | 90% fewer DB queries | Medium | 30 min |
| Optimize Algorithms | 99% faster recommendations | Hard | 45 min |
| Parallel Operations | 50% faster page loads | Easy | 20 min |

**Total Expected Improvement:** 10-50x faster, 90% cost reduction

---

## 🔧 Solution 1: Database Indexes

### Problem
No indexes on frequently queried columns causing full table scans.

### Solution: Add Indexes

**File:** `scripts/add_indexes.sql`

```sql
-- Index for user's videos
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);

-- Index for video timeline ordering
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);

-- Index for video status filtering
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);

-- Composite index for user's published videos
CREATE INDEX IF NOT EXISTS idx_videos_user_status ON videos(user_id, status, created_at DESC);

-- Index for views tracking
CREATE INDEX IF NOT EXISTS idx_views_video_id ON views(video_id);
CREATE INDEX IF NOT EXISTS idx_views_user_id ON views(user_id);

-- Composite index for duplicate view checks
CREATE INDEX IF NOT EXISTS idx_views_video_user ON views(video_id, user_id);

-- Index for comments
CREATE INDEX IF NOT EXISTS idx_comments_video_id ON comments(video_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);

-- Index for likes
CREATE INDEX IF NOT EXISTS idx_likes_video_id ON likes(video_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);

-- Composite index for duplicate like checks
CREATE INDEX IF NOT EXISTS idx_likes_video_user ON likes(video_id, user_id);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_videos_search ON videos USING GIN(to_tsvector('english', title || ' ' || description));

-- Index for tags (if using array column)
CREATE INDEX IF NOT EXISTS idx_videos_tags ON videos USING GIN(tags);
```

**Apply the indexes:**
```bash
docker exec -i streamvibe-postgres psql -U admin -d streamvibe < scripts/add_indexes.sql
```

**Verification:**
```sql
-- Check indexes
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Verify index usage
EXPLAIN ANALYZE SELECT * FROM videos WHERE user_id = 1;
-- Should show "Index Scan using idx_videos_user_id"
```

**Performance Impact:**
- Query time: 5000ms → 50ms (100x faster)
- Full table scans eliminated

---

## 🔧 Solution 2: Fix N+1 Queries

### Problem 1: Video Details Endpoint (5 queries → 1 query)

**Before (N+1 queries):**
```javascript
// src/server.js - SLOW
app.get('/api/videos/:id', async (req, res) => {
  const video = await pgPool.query('SELECT * FROM videos WHERE id = $1', [id]);
  const user = await pgPool.query('SELECT * FROM users WHERE id = $1', [video.user_id]);
  const likes = await pgPool.query('SELECT COUNT(*) FROM likes WHERE video_id = $1', [id]);
  const comments = await pgPool.query('SELECT COUNT(*) FROM comments WHERE video_id = $1', [id]);
  const views = await pgPool.query('SELECT COUNT(*) FROM views WHERE video_id = $1', [id]);
  // 5 separate queries!
});
```

**After (Single JOIN query):**
```javascript
// src/server.js - OPTIMIZED
app.get('/api/videos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pgPool.query(`
      SELECT 
        v.*,
        u.id as user_id,
        u.username,
        u.avatar,
        u.verified,
        COUNT(DISTINCT l.id) as like_count,
        COUNT(DISTINCT c.id) as comment_count,
        COUNT(DISTINCT vw.id) as view_count
      FROM videos v
      LEFT JOIN users u ON v.user_id = u.id
      LEFT JOIN likes l ON v.id = l.video_id
      LEFT JOIN comments c ON v.id = c.video_id
      LEFT JOIN views vw ON v.id = vw.video_id
      WHERE v.id = $1
      GROUP BY v.id, u.id, u.username, u.avatar, u.verified
    `, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    const video = result.rows[0];
    res.json(video);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

**Performance Impact:**
- Queries: 5 → 1
- Response time: 500ms → 50ms (10x faster)

### Problem 2: Video List Endpoint (N+1 queries)

**Before (100k+ queries):**
```javascript
app.get('/api/videos', async (req, res) => {
  const videos = await pgPool.query('SELECT * FROM videos');
  // Returns ALL 100k+ videos!
  
  for (const video of videos.rows) {
    const user = await pgPool.query('SELECT username FROM users WHERE id = $1', [video.user_id]);
    video.username = user.rows[0].username;
  }
  // N+1 queries: 1 + 100k = disaster!
});
```

**After (1 query with pagination):**
```javascript
app.get('/api/videos', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;
    
    // Get total count for pagination metadata
    const countResult = await pgPool.query('SELECT COUNT(*) as total FROM videos WHERE status = $1', ['published']);
    const totalVideos = parseInt(countResult.rows[0].total);
    
    // Get paginated videos with user info
    const result = await pgPool.query(`
      SELECT 
        v.id,
        v.title,
        v.description,
        v.thumbnail_url,
        v.duration,
        v.created_at,
        u.id as user_id,
        u.username,
        u.avatar,
        COUNT(DISTINCT l.id) as like_count,
        COUNT(DISTINCT vw.id) as view_count
      FROM videos v
      LEFT JOIN users u ON v.user_id = u.id
      LEFT JOIN likes l ON v.id = l.video_id
      LEFT JOIN views vw ON v.id = vw.video_id
      WHERE v.status = $1
      GROUP BY v.id, u.id, u.username, u.avatar
      ORDER BY v.created_at DESC
      LIMIT $2 OFFSET $3
    `, ['published', limit, offset]);
    
    res.json({
      videos: result.rows,
      pagination: {
        page,
        limit,
        total: totalVideos,
        totalPages: Math.ceil(totalVideos / limit)
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

**Performance Impact:**
- Queries: 100k+ → 1
- Data transfer: 100k records → 20 records
- Response time: 10000ms → 100ms (100x faster)

---

## 🔧 Solution 3: Implement Caching

### Problem
No caching, hitting database on every request.

### Solution: Redis Caching Layer

**Update videoCache.js:**
```javascript
// src/cache/videoCache.js - COMPLETE IMPLEMENTATION
const redis = require('redis');

class VideoCache {
  constructor() {
    this.client = redis.createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD
    });
    
    this.client.on('error', (err) => {
      console.error('Redis error:', err);
    });
    
    this.client.on('connect', () => {
      console.log('✅ Redis connected');
    });
    
    this.client.connect().catch(console.error);
    
    // Cache statistics
    this.hits = 0;
    this.misses = 0;
  }
  
  async getVideo(videoId) {
    const key = `video:${videoId}`;
    try {
      const cached = await this.client.get(key);
      
      if (cached) {
        this.hits++;
        return JSON.parse(cached);
      }
      
      this.misses++;
      return null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }
  
  async setVideo(videoId, data, ttl = 3600) {
    const key = `video:${videoId}`;
    try {
      await this.client.setEx(key, ttl, JSON.stringify(data));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }
  
  async invalidateVideo(videoId) {
    const key = `video:${videoId}`;
    try {
      await this.client.del(key);
    } catch (error) {
      console.error('Cache invalidate error:', error);
    }
  }
  
  async getTrending(ttl = 300) {
    const key = 'videos:trending';
    try {
      const cached = await this.client.get(key);
      if (cached) {
        this.hits++;
        return JSON.parse(cached);
      }
      this.misses++;
      return null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }
  
  async setTrending(data, ttl = 300) {
    const key = 'videos:trending';
    try {
      await this.client.setEx(key, ttl, JSON.stringify(data));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }
  
  // Batch view count updates
  async incrementViewCount(videoId) {
    const key = `views:pending:${videoId}`;
    try {
      await this.client.incr(key);
    } catch (error) {
      console.error('View increment error:', error);
    }
  }
  
  async flushViewCounts() {
    try {
      const keys = await this.client.keys('views:pending:*');
      const updates = [];
      
      for (const key of keys) {
        const videoId = key.split(':')[2];
        const count = await this.client.get(key);
        
        if (count) {
          updates.push({ videoId, count: parseInt(count) });
          await this.client.del(key);
        }
      }
      
      return updates;
    } catch (error) {
      console.error('Flush view counts error:', error);
      return [];
    }
  }
  
  getCacheStats() {
    const total = this.hits + this.misses;
    const hitRate = total > 0 ? (this.hits / total * 100).toFixed(2) : 0;
    
    return {
      hits: this.hits,
      misses: this.misses,
      total,
      hitRate: `${hitRate}%`
    };
  }
}

module.exports = new VideoCache();
```

**Update server.js to use cache:**
```javascript
const videoCache = require('./cache/videoCache');

// Video details with caching
app.get('/api/videos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Try cache first
    const cached = await videoCache.getVideo(id);
    if (cached) {
      return res.json(cached);
    }
    
    // Cache miss - query database
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
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    const video = result.rows[0];
    
    // Cache for 1 hour
    await videoCache.setVideo(id, video, 3600);
    
    res.json(video);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Cache statistics endpoint
app.get('/api/cache/stats', (req, res) => {
  res.json(videoCache.getCacheStats());
});
```

**Performance Impact:**
- Cache hit rate: 80-90%
- Cached requests: 5ms (vs 50ms database)
- Database load: -80%

---

## 🔧 Solution 4: Optimize Recommendation Algorithm

### Problem
O(n²) algorithm loading all 100k videos.

**Before (O(n²) - Extremely slow):**
```javascript
app.get('/api/recommendations/:userId', async (req, res) => {
  const allVideos = await pgPool.query('SELECT * FROM videos'); // 100k records!
  const watchedIds = await pgPool.query('SELECT video_id FROM views WHERE user_id = $1', [userId]);
  
  // O(n²) algorithm
  const scores = [];
  for (const video of allVideos.rows) {
    let score = 0;
    for (const watchedId of watchedIds.rows) {
      const similarity = await calculateSimilarity(video.id, watchedId); // Query in loop!
      score += similarity;
    }
    scores.push({ video, score });
  }
  
  scores.sort((a, b) => b.score - a.score);
  res.json(scores.slice(0, 20));
});
```

**After (O(n log n) - Optimized):**
```javascript
const feedCache = require('./cache/feedCache');

app.get('/api/recommendations/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Check cache first
    const cached = await feedCache.getRecommendations(userId);
    if (cached) {
      return res.json(cached);
    }
    
    // Get user's watched videos and preferences
    const watchedResult = await pgPool.query(`
      SELECT v.tags, v.category
      FROM views vw
      JOIN videos v ON vw.video_id = v.id
      WHERE vw.user_id = $1
      ORDER BY vw.created_at DESC
      LIMIT 50
    `, [userId]);
    
    if (watchedResult.rows.length === 0) {
      // New user - return trending videos
      return res.json(await getTrendingVideos());
    }
    
    // Extract user preferences
    const tagCounts = {};
    const categoryCounts = {};
    
    watchedResult.rows.forEach(video => {
      if (video.category) {
        categoryCounts[video.category] = (categoryCounts[video.category] || 0) + 1;
      }
      if (video.tags) {
        video.tags.forEach(tag => {
          tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        });
      }
    });
    
    // Get top preferences
    const topTags = Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([tag]) => tag);
    
    const topCategories = Object.entries(categoryCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([category]) => category);
    
    // Find recommendations using database filtering
    const result = await pgPool.query(`
      SELECT 
        v.*,
        u.username,
        u.avatar,
        COUNT(DISTINCT l.id) as like_count,
        COUNT(DISTINCT vw.id) as view_count,
        -- Score based on tag match
        (
          SELECT COUNT(*)
          FROM unnest(v.tags) AS tag
          WHERE tag = ANY($3::text[])
        ) as tag_score
      FROM videos v
      LEFT JOIN users u ON v.user_id = u.id
      LEFT JOIN likes l ON v.id = l.video_id
      LEFT JOIN views vw ON v.id = vw.video_id
      WHERE v.id NOT IN (
        SELECT video_id FROM views WHERE user_id = $1
      )
      AND v.status = 'published'
      AND (
        v.category = ANY($2::text[])
        OR v.tags && $3::text[]
      )
      GROUP BY v.id, u.id
      ORDER BY tag_score DESC, view_count DESC, v.created_at DESC
      LIMIT 20
    `, [userId, topCategories, topTags]);
    
    const recommendations = result.rows;
    
    // Cache for 30 minutes
    await feedCache.setRecommendations(userId, recommendations, 1800);
    
    res.json(recommendations);
  } catch (error) {
    console.error('Recommendations error:', error);
    res.status(500).json({ error: error.message });
  }
});

async function getTrendingVideos() {
  const result = await pgPool.query(`
    SELECT v.*, u.username, u.avatar,
      COUNT(DISTINCT l.id) as like_count,
      COUNT(DISTINCT vw.id) as view_count
    FROM videos v
    LEFT JOIN users u ON v.user_id = u.id
    LEFT JOIN likes l ON v.id = l.video_id
    LEFT JOIN views vw ON v.id = vw.video_id
    WHERE v.created_at > NOW() - INTERVAL '7 days'
    AND v.status = 'published'
    GROUP BY v.id, u.id
    ORDER BY view_count DESC, like_count DESC
    LIMIT 20
  `);
  
  return result.rows;
}
```

**Performance Impact:**
- Algorithm: O(n²) → O(n log n)
- Response time: 15000ms → 200ms (75x faster)
- Database queries: 1000+ → 2

---

## 🔧 Solution 5: Parallel Operations

### Problem
Sequential queries that could run in parallel.

**Before (Sequential - 400ms):**
```javascript
app.get('/api/videos/:id/page', async (req, res) => {
  const video = await getVideo(id);        // 100ms
  const comments = await getComments(id);  // 100ms
  const related = await getRelated(id);    // 100ms
  const user = await getUser(video.user_id); // 100ms
  // Total: 400ms
});
```

**After (Parallel - 100ms):**
```javascript
app.get('/api/videos/:id/page', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Execute all queries in parallel
    const [video, comments, related] = await Promise.all([
      getVideoOptimized(id),
      getCommentsOptimized(id, 20),  // With limit
      getRelatedVideos(id, 10)        // With limit
    ]);
    
    if (!video) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    // User data already included in video query
    res.json({
      video,
      comments,
      related
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

async function getVideoOptimized(id) {
  const cached = await videoCache.getVideo(id);
  if (cached) return cached;
  
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
  
  const video = result.rows[0];
  if (video) await videoCache.setVideo(id, video);
  return video;
}

async function getCommentsOptimized(videoId, limit = 20) {
  const result = await pgPool.query(`
    SELECT c.*, u.username, u.avatar
    FROM comments c
    LEFT JOIN users u ON c.user_id = u.id
    WHERE c.video_id = $1
    ORDER BY c.created_at DESC
    LIMIT $2
  `, [videoId, limit]);
  
  return result.rows;
}

async function getRelatedVideos(videoId, limit = 10) {
  const result = await pgPool.query(`
    SELECT v.*, u.username,
      COUNT(DISTINCT l.id) as like_count,
      COUNT(DISTINCT vw.id) as view_count
    FROM videos v
    LEFT JOIN users u ON v.user_id = u.id
    LEFT JOIN likes l ON v.id = l.video_id
    LEFT JOIN views vw ON v.id = vw.video_id
    WHERE v.category = (SELECT category FROM videos WHERE id = $1)
    AND v.id != $1
    AND v.status = 'published'
    GROUP BY v.id, u.id
    ORDER BY view_count DESC
    LIMIT $2
  `, [videoId, limit]);
  
  return result.rows;
}
```

**Performance Impact:**
- Response time: 400ms → 100ms (4x faster)
- Concurrent execution of independent queries

---

## 🔧 Solution 6: Search Optimization

### Problem
Full table scan with LIKE queries.

**After (Full-text search):**
```javascript
app.get('/api/search', async (req, res) => {
  try {
    const { q, page = 1, limit = 20 } = req.query;
    
    if (!q || q.length < 2) {
      return res.status(400).json({ error: 'Search query too short' });
    }
    
    const offset = (page - 1) * limit;
    
    // Use PostgreSQL full-text search
    const result = await pgPool.query(`
      SELECT 
        v.*,
        u.username,
        u.avatar,
        COUNT(DISTINCT l.id) as like_count,
        COUNT(DISTINCT vw.id) as view_count,
        ts_rank(
          to_tsvector('english', v.title || ' ' || v.description),
          plainto_tsquery('english', $1)
        ) as relevance
      FROM videos v
      LEFT JOIN users u ON v.user_id = u.id
      LEFT JOIN likes l ON v.id = l.video_id
      LEFT JOIN views vw ON v.id = vw.video_id
      WHERE to_tsvector('english', v.title || ' ' || v.description) @@ plainto_tsquery('english', $1)
      AND v.status = 'published'
      GROUP BY v.id, u.id
      ORDER BY relevance DESC, view_count DESC
      LIMIT $2 OFFSET $3
    `, [q, limit, offset]);
    
    res.json({
      results: result.rows,
      query: q,
      page: parseInt(page),
      limit: parseInt(limit)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

**Performance Impact:**
- Search time: 8000ms → 200ms (40x faster)
- Uses GIN index for full-text search

---

## 📊 Complete Performance Results

### Before Optimization
```
Endpoint                  | P95 Response | Error Rate | Queries
--------------------------|--------------|------------|--------
GET /api/videos          | 10,000ms     | 5%         | 100k+
GET /api/videos/:id      | 5,000ms      | 2%         | 5
GET /api/search          | 8,000ms      | 3%         | 1
GET /api/recommendations | 15,000ms     | 8%         | 1000+
GET /api/videos/:id/page | 2,000ms      | 1%         | 4
```

### After Optimization
```
Endpoint                  | P95 Response | Error Rate | Queries | Improvement
--------------------------|--------------|------------|---------|------------
GET /api/videos          | 100ms        | 0.1%       | 1       | 100x faster
GET /api/videos/:id      | 5ms (cached) | 0%         | 1       | 1000x faster
GET /api/search          | 200ms        | 0%         | 1       | 40x faster
GET /api/recommendations | 200ms        | 0%         | 2       | 75x faster
GET /api/videos/:id/page | 100ms        | 0%         | 3       | 20x faster
```

### Resource Savings
- **Database queries:** -95%
- **Response time:** -98%
- **Error rate:** -95%
- **Infrastructure cost:** -80%
- **User satisfaction:** +200%

---

## ✅ Verification Checklist

### Database
- [ ] All indexes created and verified
- [ ] No full table scans in EXPLAIN ANALYZE
- [ ] All queries < 50ms
- [ ] Pagination on all list endpoints

### Caching
- [ ] Redis connected
- [ ] Cache hit rate > 80%
- [ ] Cache invalidation working
- [ ] Cache statistics endpoint working

### Code Quality
- [ ] No N+1 queries
- [ ] No O(n²) algorithms
- [ ] Parallel execution where possible
- [ ] Error handling complete

### Load Testing
- [ ] All endpoints P95 < 500ms
- [ ] Error rate < 1%
- [ ] Throughput > 100 req/s
- [ ] Can handle 100 concurrent users

---

## 🎓 Key Takeaways

1. **Measure First:** Always benchmark before optimizing
2. **Database Matters:** Indexes and query optimization are critical
3. **Cache Wisely:** Cache expensive operations, not everything
4. **Paginate Everything:** Never return all records
5. **Think Parallel:** Independent operations can run concurrently
6. **Algorithm Complexity:** O(n²) is never acceptable at scale

---

**Congratulations!** You've successfully optimized a production application from unusable to performant. These patterns apply to most web applications at scale.
