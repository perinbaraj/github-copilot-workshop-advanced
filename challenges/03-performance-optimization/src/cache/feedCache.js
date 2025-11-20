const redis = require('redis');

class FeedCache {
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
  
  // Cache personalized feed
  async getFeed(userId, page = 1) {
    const key = `feed:user:${userId}:page:${page}`;
    const cached = await this.client.get(key);
    
    if (cached) {
      return JSON.parse(cached);
    }
    
    return null;
  }
  
  async setFeed(userId, page, data, ttl = 600) {
    const key = `feed:user:${userId}:page:${page}`;
    await this.client.setEx(key, ttl, JSON.stringify(data));
  }
  
  async invalidateUserFeed(userId) {
    // Invalidate all pages of user feed
    const pattern = `feed:user:${userId}:page:*`;
    const keys = await this.client.keys(pattern);
    
    if (keys.length > 0) {
      await this.client.del(keys);
    }
  }
  
  // Cache recommended videos
  async getRecommendations(userId) {
    const key = `recommendations:${userId}`;
    const cached = await this.client.get(key);
    
    if (cached) {
      return JSON.parse(cached);
    }
    
    return null;
  }
  
  async setRecommendations(userId, data, ttl = 1800) {
    const key = `recommendations:${userId}`;
    await this.client.setEx(key, ttl, JSON.stringify(data));
  }
}

module.exports = new FeedCache();
