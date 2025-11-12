-- StreamVibe Database Schema

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    avatar VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Videos table (MISSING INDEX on user_id, created_at)
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Views table (MISSING COMPOSITE INDEX)
CREATE TABLE views (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    user_id INTEGER REFERENCES users(id),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Likes table (MISSING INDEX)
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(video_id, user_id)
);

-- Comments table (MISSING INDEX on video_id, created_at)
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Video tags (MISSING INDEXES)
CREATE TABLE video_tags (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    tag VARCHAR(50) NOT NULL
);

-- Subscriptions table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER REFERENCES users(id),
    channel_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subscriber_id, channel_id)
);

-- Insert sample data
INSERT INTO users (username, email, avatar, bio) VALUES
('john_doe', 'john@example.com', 'https://example.com/avatars/1.jpg', 'Content creator'),
('jane_smith', 'jane@example.com', 'https://example.com/avatars/2.jpg', 'Tech enthusiast'),
('bob_wilson', 'bob@example.com', 'https://example.com/avatars/3.jpg', 'Gaming streamer');

-- Insert sample videos
INSERT INTO videos (user_id, title, description, video_url, thumbnail_url, duration) VALUES
(1, 'Introduction to Node.js Performance', 'Learn about Node.js optimization', 'https://cdn.example.com/v1.mp4', 'https://cdn.example.com/t1.jpg', 1200),
(1, 'Database Indexing Basics', 'Understanding database indexes', 'https://cdn.example.com/v2.mp4', 'https://cdn.example.com/t2.jpg', 900),
(2, 'Redis Caching Strategies', 'How to use Redis effectively', 'https://cdn.example.com/v3.mp4', 'https://cdn.example.com/t3.jpg', 1500),
(2, 'Microservices Architecture', 'Building scalable microservices', 'https://cdn.example.com/v4.mp4', 'https://cdn.example.com/t4.jpg', 1800),
(3, 'Gaming Performance Tips', 'Optimize your gaming experience', 'https://cdn.example.com/v5.mp4', 'https://cdn.example.com/t5.jpg', 600);

-- Insert sample views
INSERT INTO views (video_id, user_id) VALUES
(1, 2), (1, 3), (2, 2), (2, 3), (3, 1), (3, 3), (4, 1), (5, 1), (5, 2);

-- Insert sample likes
INSERT INTO likes (video_id, user_id) VALUES
(1, 2), (1, 3), (2, 3), (3, 1), (4, 1), (5, 2);

-- Insert sample comments
INSERT INTO comments (video_id, user_id, content) VALUES
(1, 2, 'Great tutorial!'),
(1, 3, 'Very helpful, thanks!'),
(2, 3, 'Clear explanation'),
(3, 1, 'This saved me hours'),
(5, 2, 'Awesome content!');

-- Insert sample tags
INSERT INTO video_tags (video_id, tag) VALUES
(1, 'nodejs'), (1, 'performance'), (1, 'tutorial'),
(2, 'database'), (2, 'indexing'), (2, 'performance'),
(3, 'redis'), (3, 'caching'), (3, 'performance'),
(4, 'microservices'), (4, 'architecture'),
(5, 'gaming'), (5, 'tips');

-- Insert sample subscriptions
INSERT INTO subscriptions (subscriber_id, channel_id) VALUES
(2, 1), (3, 1), (1, 2), (3, 2);
