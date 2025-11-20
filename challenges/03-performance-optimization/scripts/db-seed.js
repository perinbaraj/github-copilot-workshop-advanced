-- Seed data for StreamVibe performance testing

-- Insert sample users (100 users)
INSERT INTO users (username, email, password_hash, avatar, subscriber_count, verified)
SELECT 
  'user' || generate_series AS username,
  'user' || generate_series || '@example.com' AS email,
  md5(random()::text) AS password_hash,
  'https://i.pravatar.cc/150?img=' || generate_series AS avatar,
  floor(random() * 10000)::int AS subscriber_count,
  (random() > 0.8)::boolean AS verified
FROM generate_series(1, 100);

-- Insert sample videos (1000 videos)
INSERT INTO videos (title, description, user_id, duration, views, likes, video_url, thumbnail_url, category, tags)
SELECT 
  'Video Title ' || generate_series AS title,
  'This is a description for video ' || generate_series AS description,
  (floor(random() * 100) + 1)::int AS user_id,
  (floor(random() * 3600) + 60)::int AS duration,
  floor(random() * 1000000)::int AS views,
  floor(random() * 50000)::int AS likes,
  'https://example.com/videos/' || generate_series || '.mp4' AS video_url,
  'https://example.com/thumbnails/' || generate_series || '.jpg' AS thumbnail_url,
  CASE (random() * 5)::int
    WHEN 0 THEN 'Gaming'
    WHEN 1 THEN 'Music'
    WHEN 2 THEN 'Education'
    WHEN 3 THEN 'Entertainment'
    WHEN 4 THEN 'Technology'
    ELSE 'Other'
  END AS category,
  ARRAY['tag1', 'tag2', 'tag3'] AS tags
FROM generate_series(1, 1000);

-- Insert sample comments (10000 comments)
INSERT INTO comments (video_id, user_id, content, likes)
SELECT 
  (floor(random() * 1000) + 1)::int AS video_id,
  (floor(random() * 100) + 1)::int AS user_id,
  'This is a comment number ' || generate_series AS content,
  floor(random() * 1000)::int AS likes
FROM generate_series(1, 10000);

-- Insert sample views (50000 views)
INSERT INTO views (video_id, user_id, watch_duration, ip_address)
SELECT 
  (floor(random() * 1000) + 1)::int AS video_id,
  (floor(random() * 100) + 1)::int AS user_id,
  floor(random() * 3600)::int AS watch_duration,
  (floor(random() * 255) + 1)::text || '.' ||
  (floor(random() * 255) + 1)::text || '.' ||
  (floor(random() * 255) + 1)::text || '.' ||
  (floor(random() * 255) + 1)::text AS ip_address
FROM generate_series(1, 50000);

-- Update video view counts
UPDATE videos v
SET views = (
  SELECT COUNT(*) 
  FROM views 
  WHERE video_id = v.id
);

-- Update comment counts (add column if needed)
-- ALTER TABLE videos ADD COLUMN IF NOT EXISTS comment_count INTEGER DEFAULT 0;
UPDATE videos v
SET comment_count = (
  SELECT COUNT(*) 
  FROM comments 
  WHERE video_id = v.id
)
WHERE EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'videos' AND column_name = 'comment_count');

ANALYZE videos;
ANALYZE comments;
ANALYZE views;
ANALYZE users;
