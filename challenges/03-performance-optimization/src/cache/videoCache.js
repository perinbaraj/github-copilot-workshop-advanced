const redis = require('redis');

class VideoCache {
  constructor() {
    this.client = redis.createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379
    });
    
    this.client.on('error', (err) => {
      console.error('Redis error:', err);
    });
    
    this.client.connect().catch(console.error);
  }
  
  // PERFORMANCE FIX: Cache video details
  async getVideo(videoId) {
    const key = `video:${videoId}`;
    const cached = await this.client.get(key);
    
    if (cached) {
      return JSON.parse(cached);
    }
    
    return null;
  }
  
  async setVideo(videoId, data, ttl = 3600) {
    const key = `video:${videoId}`;
    await this.client.setEx(key, ttl, JSON.stringify(data));
  }
  
  async invalidateVideo(videoId) {
    const key = `video:${videoId}`;
    await this.client.del(key);
  }
  
  // PERFORMANCE FIX: Cache trending videos
  async getTrending() {
    const key = 'videos:trending';
    const cached = await this.client.get(key);
    
    if (cached) {
      return JSON.parse(cached);
    }
    
    return null;
  }
  
  async setTrending(data, ttl = 300) {
    const key = 'videos:trending';
    await this.client.setEx(key, ttl, JSON.stringify(data));
  }
  
  // PERFORMANCE FIX: Cache user feed
  async getUserFeed(userId) {
    const key = `feed:${userId}`;
    const cached = await this.client.get(key);
    
    if (cached) {
      return JSON.parse(cached);
    }
    
    return null;
  }
  
  async setUserFeed(userId, data, ttl = 600) {
    const key = `feed:${userId}`;
    await this.client.setEx(key, ttl, JSON.stringify(data));
  }
  
  // Increment view count in Redis (batch update to DB later)
  async incrementViewCount(videoId) {
    const key = `views:count:${videoId}`;
    await this.client.incr(key);
  }
  
  async getViewCount(videoId) {
    const key = `views:count:${videoId}`;
    const count = await this.client.get(key);
    return parseInt(count || '0', 10);
  }
}

module.exports = new VideoCache();
