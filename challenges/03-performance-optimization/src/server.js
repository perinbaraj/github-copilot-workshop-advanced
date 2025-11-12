const express = require('express');
const { Pool } = require('pg');
const { MongoClient } = require('mongodb');
const redis = require('redis');

const app = express();
const PORT = process.env.PORT || 3000;

// PERFORMANCE ISSUE: No connection pool configuration
const pgPool = new Pool({
  host: 'localhost',
  database: 'streamvibe',
  user: 'admin',
  password: 'admin123'
});

// PERFORMANCE ISSUE: Creating new MongoDB connections on every request
const mongoUri = 'mongodb://localhost:27017/streamvibe';
let mongoClient;

// PERFORMANCE ISSUE: Redis not being used for caching
const redisClient = redis.createClient();

app.use(express.json());

// PERFORMANCE ISSUE: N+1 query problem
app.get('/api/videos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Get video details
    const videoResult = await pgPool.query(
      'SELECT * FROM videos WHERE id = $1',
      [id]
    );
    
    if (videoResult.rows.length === 0) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    const video = videoResult.rows[0];
    
    // PERFORMANCE ISSUE: Separate query for user info
    const userResult = await pgPool.query(
      'SELECT id, username, avatar FROM users WHERE id = $1',
      [video.user_id]
    );
    video.user = userResult.rows[0];
    
    // PERFORMANCE ISSUE: Separate query for like count
    const likeResult = await pgPool.query(
      'SELECT COUNT(*) as count FROM likes WHERE video_id = $1',
      [id]
    );
    video.likeCount = parseInt(likeResult.rows[0].count);
    
    // PERFORMANCE ISSUE: Separate query for comment count
    const commentResult = await pgPool.query(
      'SELECT COUNT(*) as count FROM comments WHERE video_id = $1',
      [id]
    );
    video.commentCount = parseInt(commentResult.rows[0].count);
    
    // PERFORMANCE ISSUE: Separate query for view count
    const viewResult = await pgPool.query(
      'SELECT COUNT(*) as count FROM views WHERE video_id = $1',
      [id]
    );
    video.viewCount = parseInt(viewResult.rows[0].count);
    
    res.json(video);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: No pagination, returns ALL videos
app.get('/api/videos', async (req, res) => {
  try {
    // Returns all 100k+ videos!
    const result = await pgPool.query(
      'SELECT * FROM videos ORDER BY created_at DESC'
    );
    
    // PERFORMANCE ISSUE: Loading all data for each video (N+1 issue)
    for (const video of result.rows) {
      const userResult = await pgPool.query(
        'SELECT username FROM users WHERE id = $1',
        [video.user_id]
      );
      video.username = userResult.rows[0].username;
    }
    
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: Inefficient search without indexes
app.get('/api/search', async (req, res) => {
  try {
    const { q } = req.query;
    
    // PERFORMANCE ISSUE: Full table scan with LIKE
    // PERFORMANCE ISSUE: No full-text search index
    const result = await pgPool.query(
      `SELECT * FROM videos 
       WHERE title LIKE $1 OR description LIKE $1 
       ORDER BY created_at DESC`,
      [`%${q}%`]
    );
    
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: Expensive recommendation algorithm
app.get('/api/recommendations/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // PERFORMANCE ISSUE: Loading ALL videos (100k+)
    const allVideosResult = await pgPool.query('SELECT * FROM videos');
    const allVideos = allVideosResult.rows;
    
    // PERFORMANCE ISSUE: Getting user watch history
    const historyResult = await pgPool.query(
      'SELECT video_id FROM views WHERE user_id = $1',
      [userId]
    );
    const watchedIds = historyResult.rows.map(r => r.video_id);
    
    // PERFORMANCE ISSUE: O(n²) algorithm
    const scores = [];
    for (const video of allVideos) {
      if (watchedIds.includes(video.id)) continue;
      
      let score = 0;
      for (const watchedId of watchedIds) {
        // Check similarity (extremely inefficient)
        const similarityResult = await pgPool.query(
          'SELECT COUNT(*) as count FROM video_tags WHERE video_id = $1 AND tag IN (SELECT tag FROM video_tags WHERE video_id = $2)',
          [video.id, watchedId]
        );
        score += parseInt(similarityResult.rows[0].count);
      }
      
      scores.push({ video, score });
    }
    
    // Sort and return top 20
    scores.sort((a, b) => b.score - a.score);
    const recommendations = scores.slice(0, 20).map(s => s.video);
    
    res.json(recommendations);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PERFORMANCE ISSUE: Synchronous operations that could be parallel
app.get('/api/videos/:id/page', async (req, res) => {
  try {
    const { id } = req.params;
    
    // These are independent operations but done sequentially
    const video = await getVideo(id);
    const comments = await getComments(id);
    const related = await getRelatedVideos(id);
    const user = await getUser(video.user_id);
    
    res.json({ video, comments, related, user });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

async function getVideo(id) {
  const result = await pgPool.query('SELECT * FROM videos WHERE id = $1', [id]);
  return result.rows[0];
}

async function getComments(videoId) {
  // PERFORMANCE ISSUE: No limit on comments
  const result = await pgPool.query(
    'SELECT * FROM comments WHERE video_id = $1 ORDER BY created_at DESC',
    [videoId]
  );
  return result.rows;
}

async function getRelatedVideos(videoId) {
  // PERFORMANCE ISSUE: Inefficient similarity query
  const result = await pgPool.query(
    'SELECT * FROM videos WHERE id != $1 LIMIT 10',
    [videoId]
  );
  return result.rows;
}

async function getUser(userId) {
  const result = await pgPool.query('SELECT * FROM users WHERE id = $1', [userId]);
  return result.rows[0];
}

// PERFORMANCE ISSUE: No graceful shutdown
app.listen(PORT, () => {
  console.log(`StreamVibe running on port ${PORT}`);
});

module.exports = app;
