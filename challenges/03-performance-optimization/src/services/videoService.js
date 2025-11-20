/**
 * Video Service - Business Logic
 * 
 * PERFORMANCE ISSUES:
 * 1. Expensive view count calculations
 * 2. No caching of aggregated data
 * 3. Sequential operations that could be parallel
 */

const { pool } = require('../config/database');

/**
 * Get video with all metadata
 * 
 * PERFORMANCE ISSUE: N+1 queries for metadata
 */
async function getVideoWithMetadata(videoId) {
  // Get video
  const videoResult = await pool.query(
    'SELECT * FROM videos WHERE id = $1',
    [videoId]
  );
  
  if (videoResult.rows.length === 0) {
    return null;
  }
  
  const video = videoResult.rows[0];
  
  // PERFORMANCE ISSUE: Sequential queries
  // These could be done in parallel with Promise.all()
  
  const userResult = await pool.query(
    'SELECT id, username, avatar FROM users WHERE id = $1',
    [video.user_id]
  );
  video.user = userResult.rows[0];
  
  const likesResult = await pool.query(
    'SELECT COUNT(*) as count FROM likes WHERE video_id = $1',
    [videoId]
  );
  video.likeCount = parseInt(likesResult.rows[0].count);
  
  const viewsResult = await pool.query(
    'SELECT COUNT(*) as count FROM views WHERE video_id = $1',
    [videoId]
  );
  video.viewCount = parseInt(viewsResult.rows[0].count);
  
  const commentsResult = await pool.query(
    'SELECT COUNT(*) as count FROM comments WHERE video_id = $1',
    [videoId]
  );
  video.commentCount = parseInt(commentsResult.rows[0].count);
  
  return video;
}

/**
 * Record video view
 * 
 * PERFORMANCE ISSUE: Updates view count synchronously
 */
async function recordView(videoId, userId, watchTime) {
  // Insert view record
  await pool.query(
    `INSERT INTO views (video_id, user_id, watch_time, created_at)
     VALUES ($1, $2, $3, NOW())`,
    [videoId, userId, watchTime]
  );
  
  // PERFORMANCE ISSUE: Update view count synchronously
  // Should be done asynchronously or via database trigger
  await pool.query(
    'UPDATE videos SET view_count = view_count + 1 WHERE id = $1',
    [videoId]
  );
}

/**
 * Get trending videos
 * 
 * PERFORMANCE ISSUE: Expensive aggregation on every request
 */
async function getTrendingVideos(limit = 20) {
  // PERFORMANCE ISSUE: Complex aggregation with no caching
  // This query scans millions of rows
  const result = await pool.query(
    `SELECT v.*, 
            COUNT(DISTINCT vw.id) as view_count,
            COUNT(DISTINCT l.id) as like_count
     FROM videos v
     LEFT JOIN views vw ON v.id = vw.video_id 
                        AND vw.created_at > NOW() - INTERVAL '7 days'
     LEFT JOIN likes l ON v.id = l.video_id
     GROUP BY v.id
     ORDER BY view_count DESC, like_count DESC
     LIMIT $1`,
    [limit]
  );
  
  return result.rows;
}

module.exports = {
  getVideoWithMetadata,
  recordView,
  getTrendingVideos
};
