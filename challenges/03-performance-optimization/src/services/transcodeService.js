/**
 * Transcode Service
 * 
 * PERFORMANCE ISSUES:
 * 1. Synchronous transcode operations
 * 2. No queue system
 * 3. Blocks API requests
 * 4. No progress tracking
 */

const { pool } = require('../config/database');

/**
 * Initiate video transcode
 * 
 * PERFORMANCE ISSUE: Synchronous operation
 * Should use job queue (Bull/BullMQ)
 */
async function initiateTranscode(videoId, formats = ['720p', '1080p']) {
  console.log(`Starting transcode for video ${videoId}...`);
  
  // PERFORMANCE ISSUE: This would block for minutes!
  // In real app, this should be queued
  await simulateTranscode(videoId, formats);
  
  // Update video status
  await pool.query(
    'UPDATE videos SET status = $1 WHERE id = $2',
    ['ready', videoId]
  );
  
  console.log(`Transcode completed for video ${videoId}`);
}

/**
 * Simulate transcode operation
 */
async function simulateTranscode(videoId, formats) {
  for (const format of formats) {
    console.log(`Transcoding to ${format}...`);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Store transcode result
    await pool.query(
      `INSERT INTO video_transcodes (video_id, format, url, created_at)
       VALUES ($1, $2, $3, NOW())`,
      [videoId, format, `/videos/${videoId}/${format}.mp4`]
    );
  }
}

module.exports = {
  initiateTranscode
};
