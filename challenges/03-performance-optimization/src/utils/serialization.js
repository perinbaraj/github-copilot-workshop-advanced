/**
 * Serialization Utilities
 * 
 * PERFORMANCE ISSUES:
 * 1. Inefficient JSON serialization
 * 2. No streaming for large responses
 * 3. Includes unnecessary fields
 */

/**
 * Serialize video object
 * 
 * PERFORMANCE ISSUE: No field selection
 * Returns all fields even when not needed
 */
function serializeVideo(video) {
  return {
    id: video.id,
    title: video.title,
    description: video.description,
    url: video.url,
    thumbnail: video.thumbnail,
    duration: video.duration,
    category: video.category,
    tags: video.tags,
    viewCount: video.view_count || video.viewCount,
    likeCount: video.like_count || video.likeCount,
    commentCount: video.comment_count || video.commentCount,
    createdAt: video.created_at,
    updatedAt: video.updated_at,
    user: video.user ? serializeUser(video.user) : undefined
  };
}

/**
 * Serialize user object
 */
function serializeUser(user) {
  return {
    id: user.id,
    username: user.username,
    avatar: user.avatar,
    subscriberCount: user.subscriber_count || user.subscriberCount
  };
}

/**
 * Serialize video list
 * 
 * PERFORMANCE ISSUE: No pagination metadata
 * No cursor-based pagination support
 */
function serializeVideoList(videos) {
  return videos.map(serializeVideo);
}

/**
 * Serialize paginated response
 */
function serializePaginated(data, page, limit, total) {
  return {
    data: data,
    pagination: {
      page: page,
      limit: limit,
      total: total,
      totalPages: Math.ceil(total / limit),
      hasNext: page * limit < total,
      hasPrev: page > 1
    }
  };
}

module.exports = {
  serializeVideo,
  serializeUser,
  serializeVideoList,
  serializePaginated
};
