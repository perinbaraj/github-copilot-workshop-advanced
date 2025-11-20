/**
 * Recommendation Controller - Video Recommendations
 * 
 * PERFORMANCE ISSUES:
 * 1. O(n²) algorithm - loads ALL videos into memory
 * 2. Calculates similarity for every video pair
 * 3. No caching of recommendations
 * 4. No incremental updates
 * 5. Blocks event loop with CPU-intensive calculation
 * 
 * This is the WORST performance bottleneck in the application!
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
 * Get personalized video recommendations
 * 
 * PERFORMANCE DISASTER:
 * 1. Loads ALL 100k+ videos into memory (~500MB)
 * 2. O(n²) similarity calculation = 10 billion operations!
 * 3. Takes 15-30 seconds per request
 * 4. Blocks event loop (CPU-intensive)
 * 5. No caching (same recommendations for hours)
 * 
 * Current: 15-30 seconds, 100% CPU
 * Target: <200ms with pre-computed recommendations + caching
 */
async function getRecommendations(req, res) {
  try {
    const { userId } = req.params;
    
    console.log(`Getting recommendations for user ${userId}...`);
    console.time('recommendations');
    
    // PERFORMANCE DISASTER: Load ALL videos
    console.log('Loading all videos...');
    const allVideosResult = await pool.query(
      'SELECT * FROM videos'
    );
    const allVideos = allVideosResult.rows; // 100k+ videos!
    console.log(`Loaded ${allVideos.length} videos`);
    
    // Get user's watch history
    const watchedResult = await pool.query(
      'SELECT video_id FROM views WHERE user_id = $1',
      [userId]
    );
    const watchedVideoIds = new Set(watchedResult.rows.map(row => row.video_id));
    console.log(`User has watched ${watchedVideoIds.size} videos`);
    
    // PERFORMANCE DISASTER: O(n²) algorithm
    // For each video, calculate similarity with all other videos
    console.log('Calculating similarities...');
    const recommendations = [];
    
    for (const video of allVideos) {
      // Skip if user already watched
      if (watchedVideoIds.has(video.id)) {
        continue;
      }
      
      let similarityScore = 0;
      
      // PERFORMANCE DISASTER: Inner loop over ALL videos
      for (const watchedVideoId of watchedVideoIds) {
        const watchedVideo = allVideos.find(v => v.id === watchedVideoId);
        
        if (watchedVideo) {
          // PERFORMANCE DISASTER: Complex similarity calculation
          // This runs millions of times!
          similarityScore += calculateSimilarity(video, watchedVideo);
        }
      }
      
      recommendations.push({
        video,
        score: similarityScore
      });
    }
    
    // Sort by score
    console.log('Sorting recommendations...');
    recommendations.sort((a, b) => b.score - a.score);
    
    // Take top 20
    const topRecommendations = recommendations.slice(0, 20);
    
    // PERFORMANCE ISSUE: Another N+1 query for user data
    for (const rec of topRecommendations) {
      const userResult = await pool.query(
        'SELECT username, avatar FROM users WHERE id = $1',
        [rec.video.user_id]
      );
      rec.video.user = userResult.rows[0];
    }
    
    console.timeEnd('recommendations');
    console.log('Recommendations calculated!');
    
    res.json(topRecommendations.map(r => r.video));
  } catch (error) {
    console.error('Error getting recommendations:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Calculate similarity between two videos
 * 
 * PERFORMANCE ISSUE: This is called millions of times!
 * Should be pre-computed and stored
 */
function calculateSimilarity(video1, video2) {
  let score = 0;
  
  // Category match
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
  
  // Similar duration (within 20%)
  const durationDiff = Math.abs(video1.duration - video2.duration);
  if (durationDiff < video1.duration * 0.2) {
    score += 3;
  }
  
  // Similar popularity
  // Note: These would need to be pre-computed
  // const popularityDiff = Math.abs(video1.viewCount - video2.viewCount);
  // if (popularityDiff < 1000) {
  //   score += 2;
  // }
  
  return score;
}

/**
 * Get similar videos (based on single video)
 * 
 * PERFORMANCE ISSUE: Still inefficient, but better than full recommendations
 */
async function getSimilarVideos(req, res) {
  try {
    const { videoId } = req.params;
    
    // Get source video
    const videoResult = await pool.query(
      'SELECT * FROM videos WHERE id = $1',
      [videoId]
    );
    
    if (videoResult.rows.length === 0) {
      return res.status(404).json({ error: 'Video not found' });
    }
    
    const sourceVideo = videoResult.rows[0];
    
    // PERFORMANCE ISSUE: Load all videos to calculate similarity
    const allVideosResult = await pool.query(
      'SELECT * FROM videos WHERE id != $1 LIMIT 1000',
      [videoId]
    );
    
    const similarities = allVideosResult.rows.map(video => ({
      video,
      score: calculateSimilarity(sourceVideo, video)
    }));
    
    similarities.sort((a, b) => b.score - a.score);
    
    const similar = similarities.slice(0, 10);
    
    res.json(similar.map(s => s.video));
  } catch (error) {
    console.error('Error getting similar videos:', error);
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  getRecommendations,
  getSimilarVideos
};
