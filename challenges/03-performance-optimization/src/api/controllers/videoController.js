/**
 * Video Controller - Video Details and Listing
 * 
 * PERFORMANCE ISSUES:
 * 1. N+1 Query Problem - Separate queries for user, likes, comments, views
 * 2. No Caching - Every request hits database
 * 3. No Pagination - Returns all videos
 * 4. Sequential Queries - Could be parallelized
 * 5. No Connection Pooling - Inefficient database connections
 */

const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'streamvibe',
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || 'admin123',
  // PERFORMANCE ISSUE: Small connection pool
  max: 5,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

/**
 * Get video details with all related data
 * 
 * PERFORMANCE ISSUE: N+1 Query Problem
 * Makes 5 separate database queries for one video:
 * 1. Video details
 * 2. User info
 * 3. Like count
 * 4. Comment count
 * 5. View count
 * 
 * Should be: 1 query with JOINs
 * Current: ~500ms | Target: <50ms
 */
async function getVideoDetails(req, res) {
  try {
    const { id } = req.params;
    
    // Query 1: Get video
    const videoResult = await pool.query(
      'SELECT * FROM videos WHERE id = $1',
      [id]
    );
    
    if (videoResult.rows.length === 0) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    const video = videoResult.rows[0];
    
    // PERFORMANCE ISSUE: Separate query for user
    // Query 2: Get user
    const userResult = await pool.query(
      'SELECT id, username, avatar, verified FROM users WHERE id = $1',
      [video.user_id]
    );
    video.user = userResult.rows[0];
    
    // PERFORMANCE ISSUE: Separate query for likes
    // Query 3: Count likes
    const likesResult = await pool.query(
      'SELECT COUNT(*) as count FROM likes WHERE video_id = $1',
      [id]
    );
    video.likeCount = parseInt(likesResult.rows[0].count);
    
    // PERFORMANCE ISSUE: Separate query for comments
    // Query 4: Count comments
    const commentsResult = await pool.query(
      'SELECT COUNT(*) as count FROM comments WHERE video_id = $1',
      [id]
    );
    video.commentCount = parseInt(commentsResult.rows[0].count);
    
    // PERFORMANCE ISSUE: Separate query for views
    // Query 5: Count views
    const viewsResult = await pool.query(
      'SELECT COUNT(*) as count FROM views WHERE video_id = $1',
      [id]
    );
    video.viewCount = parseInt(viewsResult.rows[0].count);
    
    // Total queries: 5 for one video!
    // Response time: ~500ms
    
    res.json(video);
  } catch (error) {
    console.error('Error getting video:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * List all videos
 * 
 * PERFORMANCE ISSUES:
 * 1. No Pagination - Returns ALL 100k+ videos
 * 2. N+1 Query - Separate query for each video's user
 * 3. No Caching - Every request loads everything
 * 4. Loads unnecessary fields
 * 
 * Current: ~10 seconds for 100k videos
 * Target: <200ms for 20 videos with pagination
 */
async function listVideos(req, res) {
  try {
    // PERFORMANCE ISSUE: No pagination!
    // Returns ALL videos (100k+ records = ~50MB of data)
    const result = await pool.query(
      'SELECT * FROM videos ORDER BY created_at DESC'
    );
    
    // PERFORMANCE ISSUE: N+1 query for user info
    // Makes 100k additional queries!
    for (const video of result.rows) {
      const userResult = await pool.query(
        'SELECT username, avatar FROM users WHERE id = $1',
        [video.user_id]
      );
      
      if (userResult.rows.length > 0) {
        video.username = userResult.rows[0].username;
        video.avatar = userResult.rows[0].avatar;
      }
    }
    
    // Sending 100k+ records to client!
    // Response time: 10+ seconds
    // Memory usage: Huge
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error listing videos:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get trending videos
 * 
 * PERFORMANCE ISSUES:
 * 1. Expensive COUNT queries
 * 2. No materialized view
 * 3. No caching (should cache for 5 minutes)
 * 4. Calculates on every request
 */
async function getTrendingVideos(req, res) {
  try {
    // PERFORMANCE ISSUE: Expensive aggregation on every request
    const result = await pool.query(`
      SELECT v.*, 
             COUNT(DISTINCT vw.id) as view_count,
             COUNT(DISTINCT l.id) as like_count,
             u.username, u.avatar
      FROM videos v
      LEFT JOIN views vw ON v.id = vw.video_id 
        AND vw.created_at > NOW() - INTERVAL '24 hours'
      LEFT JOIN likes l ON v.id = l.video_id
      LEFT JOIN users u ON v.user_id = u.id
      WHERE v.created_at > NOW() - INTERVAL '7 days'
      GROUP BY v.id, u.id
      ORDER BY view_count DESC, like_count DESC
      LIMIT 20
    `);
    
    // This query takes 3-5 seconds on 100k videos
    // Should be: Materialized view + Redis cache
    
    res.json(result.rows);
  } catch (error) {
    console.error('Error getting trending videos:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get video page data (video + comments + related videos)
 * 
 * PERFORMANCE ISSUE: Sequential queries
 * All 3 queries are independent and could run in parallel
 * 
 * Current: 300ms (3 x 100ms)
 * Target: 100ms (parallel execution)
 */
async function getVideoPage(req, res) {
  try {
    const { id } = req.params;
    
    // PERFORMANCE ISSUE: Sequential execution of independent queries
    const video = await getVideoWithDetails(id);
    const comments = await getVideoComments(id);
    const relatedVideos = await getRelatedVideos(id);
    
    // Each query waits for the previous one to complete
    // Could execute all 3 in parallel with Promise.all()
    
    res.json({
      video,
      comments,
      relatedVideos
    });
  } catch (error) {
    console.error('Error getting video page:', error);
    res.status(500).json({ error: error.message });
  }
}

async function getVideoWithDetails(id) {
  const result = await pool.query(
    'SELECT * FROM videos WHERE id = $1',
    [id]
  );
  return result.rows[0];
}

async function getVideoComments(videoId) {
  // PERFORMANCE ISSUE: No pagination on comments
  const result = await pool.query(
    'SELECT c.*, u.username, u.avatar FROM comments c JOIN users u ON c.user_id = u.id WHERE c.video_id = $1 ORDER BY c.created_at DESC',
    [videoId]
  );
  return result.rows;
}

async function getRelatedVideos(videoId) {
  // PERFORMANCE ISSUE: Inefficient similarity calculation
  const result = await pool.query(
    'SELECT * FROM videos WHERE category = (SELECT category FROM videos WHERE id = $1) AND id != $1 LIMIT 10',
    [videoId]
  );
  return result.rows;
}

module.exports = {
  getVideoDetails,
  listVideos,
  getTrendingVideos,
  getVideoPage
};
