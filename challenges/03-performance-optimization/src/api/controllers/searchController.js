/**
 * Search Controller - Video Search
 * 
 * PERFORMANCE ISSUES:
 * 1. Uses LIKE %query% (full table scan)
 * 2. No full-text search index
 * 3. No search result caching
 * 4. Searches multiple unindexed fields
 * 5. Case-sensitive search (inefficient)
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
 * Search videos
 * 
 * PERFORMANCE ISSUES:
 * 1. LIKE %query% causes full table scan on 100k+ videos
 * 2. No full-text search index (GIN index for tsvector)
 * 3. Searches multiple fields without optimization
 * 4. No caching of popular searches
 * 5. Case-insensitive search is inefficient
 * 
 * Current: 5-8 seconds for fuzzy search
 * Target: <200ms with full-text search + index
 */
async function searchVideos(req, res) {
  try {
    const { q, category, minViews } = req.query;
    
    if (!q || q.length < 2) {
      return res.status(400).json({ error: 'Query too short' });
    }
    
    // PERFORMANCE ISSUE: LIKE %query% on unindexed text fields
    // This causes a FULL TABLE SCAN on 100k+ videos
    // Query plan shows: Seq Scan on videos (cost=0.00..5000.00)
    const query = `
      SELECT v.*, u.username, u.avatar,
             (SELECT COUNT(*) FROM views WHERE video_id = v.id) as view_count,
             (SELECT COUNT(*) FROM likes WHERE video_id = v.id) as like_count
      FROM videos v
      JOIN users u ON v.user_id = u.id
      WHERE LOWER(v.title) LIKE LOWER($1)
         OR LOWER(v.description) LIKE LOWER($1)
         OR LOWER(v.tags::text) LIKE LOWER($1)
      ${category ? 'AND v.category = $2' : ''}
      ORDER BY view_count DESC
      LIMIT 50
    `;
    
    const searchPattern = `%${q}%`;
    const params = category ? [searchPattern, category] : [searchPattern];
    
    const result = await pool.query(query, params);
    
    // Query takes 5-8 seconds on 100k videos
    // Should use: PostgreSQL full-text search with GIN index
    // or: Elasticsearch for advanced search
    
    res.json({
      query: q,
      results: result.rows,
      count: result.rows.length
    });
  } catch (error) {
    console.error('Error searching videos:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Search with filters
 * 
 * PERFORMANCE ISSUE: Multiple LIKE conditions, no indexes
 */
async function advancedSearch(req, res) {
  try {
    const {
      q,
      category,
      minDuration,
      maxDuration,
      uploadedAfter,
      sortBy = 'relevance'
    } = req.query;
    
    // PERFORMANCE ISSUE: Complex query with multiple unindexed filters
    let query = `
      SELECT v.*, u.username, u.avatar,
             (SELECT COUNT(*) FROM views WHERE video_id = v.id) as view_count,
             (SELECT COUNT(*) FROM likes WHERE video_id = v.id) as like_count
      FROM videos v
      JOIN users u ON v.user_id = u.id
      WHERE 1=1
    `;
    
    const params = [];
    let paramIndex = 1;
    
    if (q) {
      query += ` AND (LOWER(v.title) LIKE LOWER($${paramIndex}) OR LOWER(v.description) LIKE LOWER($${paramIndex}))`;
      params.push(`%${q}%`);
      paramIndex++;
    }
    
    if (category) {
      query += ` AND v.category = $${paramIndex}`;
      params.push(category);
      paramIndex++;
    }
    
    if (minDuration) {
      query += ` AND v.duration >= $${paramIndex}`;
      params.push(minDuration);
      paramIndex++;
    }
    
    if (maxDuration) {
      query += ` AND v.duration <= $${paramIndex}`;
      params.push(maxDuration);
      paramIndex++;
    }
    
    if (uploadedAfter) {
      query += ` AND v.created_at >= $${paramIndex}`;
      params.push(uploadedAfter);
      paramIndex++;
    }
    
    // PERFORMANCE ISSUE: Sorting by aggregated columns is slow
    if (sortBy === 'views') {
      query += ` ORDER BY view_count DESC`;
    } else if (sortBy === 'likes') {
      query += ` ORDER BY like_count DESC`;
    } else if (sortBy === 'recent') {
      query += ` ORDER BY v.created_at DESC`;
    }
    
    query += ` LIMIT 50`;
    
    const result = await pool.query(query, params);
    
    res.json({
      results: result.rows,
      count: result.rows.length,
      filters: { q, category, minDuration, maxDuration, uploadedAfter, sortBy }
    });
  } catch (error) {
    console.error('Error in advanced search:', error);
    res.status(500).json({ error: error.message });
  }
}

/**
 * Get search suggestions (autocomplete)
 * 
 * PERFORMANCE ISSUE: No dedicated search suggestions table
 */
async function getSearchSuggestions(req, res) {
  try {
    const { q } = req.query;
    
    if (!q || q.length < 2) {
      return res.json([]);
    }
    
    // PERFORMANCE ISSUE: LIKE query on every keystroke
    const result = await pool.query(
      `SELECT DISTINCT title
       FROM videos
       WHERE LOWER(title) LIKE LOWER($1)
       LIMIT 10`,
      [`${q}%`]
    );
    
    // Should use: Trie data structure or dedicated suggestions table
    // with pre-computed popular searches
    
    res.json(result.rows.map(row => row.title));
  } catch (error) {
    console.error('Error getting suggestions:', error);
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  searchVideos,
  advancedSearch,
  getSearchSuggestions
};
