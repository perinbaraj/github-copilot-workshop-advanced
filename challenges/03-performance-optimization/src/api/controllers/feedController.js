/**
 * Feed Controller - User's Personalized Feed
 * 
 * PERFORMANCE ISSUES:
 * 1. Loads all subscriptions, then all videos
 * 2. N+1 query for video details
 * 3. No pagination
 * 4. No caching (feed rarely changes per minute)
 * 5. Sorts in application instead of database
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
 * Get user's personalized feed
 * 
 * PERFORMANCE ISSUES:
 * 1. Loads ALL subscriptions first
 * 2. Then loads ALL videos from those users
 * 3. N+1 query for each video's metadata
 * 4. Sorts in memory instead of database
 * 5. No caching (feed is same for 5+ minutes typically)
 * 
 * Current: 2-5 seconds for user with 100 subscriptions
 * Target: <200ms with caching
 */
async function getUserFeed(req, res) {
  try {
    const { userId } = req.params;
    
    // PERFORMANCE ISSUE: Load all subscriptions
    const subscriptionsResult = await pool.query(
      'SELECT channel_id FROM subscriptions WHERE user_id = $1',
      [userId]
    );
    
    const channelIds = subscriptionsResult.rows.map(row => row.channel_id);
    
    if (channelIds.length === 0) {
      return res.json([]);
    }
    
    // PERFORMANCE ISSUE: Load ALL videos from ALL subscribed channels
    // No limit, could be 10k+ videos
    const videosResult = await pool.query(
      `SELECT * FROM videos 
       WHERE user_id = ANY($1) 
       ORDER BY created_at DESC`,
      [channelIds]
    );
    
    const videos = videosResult.rows;
    
    // PERFORMANCE ISSUE: N+1 query for each video
    for (const video of videos) {
      // Get user info
      const userResult = await pool.query(
        'SELECT username, avatar FROM users WHERE id = $1',
        [video.user_id]
      );
      video.user = userResult.rows[0];
      
      // Get view count
      const viewResult = await pool.query(
        'SELECT COUNT(*) as count FROM views WHERE video_id = $1',
        [video.id]
      );
      video.viewCount = parseInt(viewResult.rows[0].count);
      
      // Get like count
      const likeResult = await pool.query(
        'SELECT COUNT(*) as count FROM likes WHERE video_id = $1',
        [video.id]
      );
      video.likeCount = parseInt(likeResult.rows[0].count);
    }
    
    // PERFORMANCE ISSUE: Sorting in application memory
    videos.sort((a, b) => {
      // Complex sorting algorithm
      const scoreA = (a.viewCount * 0.7) + (a.likeCount * 0.3);
      const scoreB = (b.viewCount * 0.7) + (b.likeCount * 0.3);
      return scoreB - scoreA;
    });
    
    // PERFORMANCE ISSUE: No pagination
    // Sending all videos (could be thousands)
    res.json(videos);
  } catch (error) {
    console.error('Error getting user feed:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get user's watch history
 * 
 * PERFORMANCE ISSUE: N+1 query pattern
 */
async function getWatchHistory(req, res) {
  try {
    const { userId } = req.params;
    
    const viewsResult = await pool.query(
      'SELECT video_id, MAX(created_at) as last_watched FROM views WHERE user_id = $1 GROUP BY video_id ORDER BY last_watched DESC LIMIT 50',
      [userId]
    );
    
    const history = [];
    
    // PERFORMANCE ISSUE: Separate query for each video
    for (const view of viewsResult.rows) {
      const videoResult = await pool.query(
        'SELECT v.*, u.username, u.avatar FROM videos v JOIN users u ON v.user_id = u.id WHERE v.id = $1',
        [view.video_id]
      );
      
      if (videoResult.rows.length > 0) {
        history.push({
          ...videoResult.rows[0],
          lastWatched: view.last_watched
        });
      }
    }
    
    res.json(history);
  } catch (error) {
    console.error('Error getting watch history:', error);
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getUserFeed,
  getWatchHistory
};
