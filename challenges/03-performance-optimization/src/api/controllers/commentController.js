/**
 * Comment Controller - Video Comments
 * 
 * PERFORMANCE ISSUES:
 * 1. No pagination on comments
 * 2. Loads all replies for all comments (N+1)
 * 3. No caching of comment counts
 * 4. Sequential queries for nested data
 */

const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'streamvibe',
  user: process.env.DB_USER || 'admin',
  password: process.env.DB_PASSWORD || 'admin123',
  max: 5
});

/**
 * Get comments for a video
 * 
 * PERFORMANCE ISSUES:
 * 1. No pagination - loads ALL comments
 * 2. N+1 query for replies
 * 3. N+1 query for like counts
 * 4. Could be 10k+ comments on popular videos
 */
async function getVideoComments(req, res) {
  try {
    const { videoId } = req.params;
    
    // PERFORMANCE ISSUE: No pagination
    // Loads ALL comments (could be 10k+)
    const commentsResult = await pool.query(
      `SELECT c.*, u.username, u.avatar
       FROM comments c
       JOIN users u ON c.user_id = u.id
       WHERE c.video_id = $1 AND c.parent_id IS NULL
       ORDER BY c.created_at DESC`,
      [videoId]
    );
    
    const comments = commentsResult.rows;
    
    // PERFORMANCE ISSUE: N+1 query for replies
    for (const comment of comments) {
      const repliesResult = await pool.query(
        `SELECT c.*, u.username, u.avatar
         FROM comments c
         JOIN users u ON c.user_id = u.id
         WHERE c.parent_id = $1
         ORDER BY c.created_at ASC`,
        [comment.id]
      );
      comment.replies = repliesResult.rows;
      
      // PERFORMANCE ISSUE: N+1 query for like count
      const likesResult = await pool.query(
        'SELECT COUNT(*) as count FROM comment_likes WHERE comment_id = $1',
        [comment.id]
      );
      comment.likeCount = parseInt(likesResult.rows[0].count);
    }
    
    res.json(comments);
  } catch (error) {
    console.error('Error getting comments:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Post a comment
 * 
 * PERFORMANCE ISSUE: Updates comment count synchronously
 */
async function postComment(req, res) {
  try {
    const { videoId } = req.params;
    const { userId, text, parentId } = req.body;
    
    // Insert comment
    const result = await pool.query(
      `INSERT INTO comments (video_id, user_id, text, parent_id, created_at)
       VALUES ($1, $2, $3, $4, NOW())
       RETURNING *`,
      [videoId, userId, text, parentId || null]
    );
    
    const comment = result.rows[0];
    
    // PERFORMANCE ISSUE: Update comment count synchronously
    // Should be done asynchronously or via database trigger
    await pool.query(
      'UPDATE videos SET comment_count = comment_count + 1 WHERE id = $1',
      [videoId]
    );
    
    res.status(201).json(comment);
  } catch (error) {
    console.error('Error posting comment:', error);
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getVideoComments,
  postComment
};
