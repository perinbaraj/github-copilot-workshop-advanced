/**
 * Recommendation Service
 * 
 * PERFORMANCE ISSUES:
 * 1. O(n²) algorithm for similarity calculation
 * 2. No pre-computation of recommendations
 * 3. No caching layer
 * 4. Loads all data into memory
 * 5. Blocks event loop with CPU-intensive work
 */

const { pool } = require('../config/database');

/**
 * Generate recommendations for user
 * 
 * PERFORMANCE DISASTER: This is the worst bottleneck!
 * - Loads 100k+ videos into memory
 * - O(n²) algorithm = 10 billion operations
 * - Takes 15-30 seconds per request
 * - No caching
 * 
 * Should use:
 * - Pre-computed similarity matrix
 * - Collaborative filtering
 * - Matrix factorization (ALS, SVD)
 * - Cache recommendations for hours
 * - Background job to update recommendations
 */
async function generateRecommendations(userId, limit = 20) {
  // Get user's watch history
  const watchedResult = await pool.query(
    'SELECT video_id, watch_time FROM views WHERE user_id = $1',
    [userId]
  );
  
  if (watchedResult.rows.length === 0) {
    // New user - return trending videos
    return getTrendingRecommendations(limit);
  }
  
  const watchedVideos = watchedResult.rows;
  
  // PERFORMANCE DISASTER: Load ALL videos
  const allVideosResult = await pool.query(
    'SELECT id, title, category, tags, user_id, duration FROM videos'
  );
  const allVideos = allVideosResult.rows;
  
  console.log(`Computing recommendations from ${allVideos.length} videos...`);
  
  // Calculate scores for each unwatched video
  const watchedIds = new Set(watchedVideos.map(v => v.video_id));
  const scores = new Map();
  
  // PERFORMANCE DISASTER: O(n²) nested loops
  for (const video of allVideos) {
    if (watchedIds.has(video.id)) {
      continue;
    }
    
    let totalScore = 0;
    
    // Compare with each watched video
    for (const watched of watchedVideos) {
      const watchedVideo = allVideos.find(v => v.id === watched.video_id);
      if (watchedVideo) {
        const similarity = calculateVideoSimilarity(video, watchedVideo);
        const watchTimeWeight = Math.min(watched.watch_time / 100, 1);
        totalScore += similarity * watchTimeWeight;
      }
    }
    
    scores.set(video.id, totalScore);
  }
  
  // Sort by score
  const sortedVideos = allVideos
    .filter(v => !watchedIds.has(v.id))
    .sort((a, b) => (scores.get(b.id) || 0) - (scores.get(a.id) || 0))
    .slice(0, limit);
  
  return sortedVideos;
}

/**
 * Calculate similarity between two videos
 * 
 * PERFORMANCE ISSUE: Called millions of times
 * Should be pre-computed and stored
 */
function calculateVideoSimilarity(video1, video2) {
  let score = 0;
  
  // Category match (high weight)
  if (video1.category === video2.category) {
    score += 10;
  }
  
  // Tags overlap
  const tags1 = video1.tags || [];
  const tags2 = video2.tags || [];
  const commonTags = tags1.filter(tag => tags2.includes(tag));
  score += commonTags.length * 5;
  
  // Same creator
  if (video1.user_id === video2.user_id) {
    score += 15;
  }
  
  // Similar duration
  const durationDiff = Math.abs(video1.duration - video2.duration);
  const durationScore = Math.max(0, 5 - (durationDiff / 60));
  score += durationScore;
  
  return score;
}

/**
 * Get trending recommendations
 */
async function getTrendingRecommendations(limit = 20) {
  const result = await pool.query(
    `SELECT v.* 
     FROM videos v
     ORDER BY v.view_count DESC, v.created_at DESC
     LIMIT $1`,
    [limit]
  );
  
  return result.rows;
}

module.exports = {
  generateRecommendations,
  calculateVideoSimilarity,
  getTrendingRecommendations
};
