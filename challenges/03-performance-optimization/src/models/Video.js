const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize(
  process.env.DB_NAME || 'streamvibe',
  process.env.DB_USER || 'admin',
  process.env.DB_PASSWORD || 'admin123',
  {
    host: process.env.DB_HOST || 'localhost',
    dialect: 'postgres',
    // PERFORMANCE ISSUE: No connection pool configuration
    pool: {
      max: 5,  // PERFORMANCE ISSUE: Too small pool
      min: 0,
      acquire: 30000,
      idle: 10000
    },
    // PERFORMANCE ISSUE: Logging all SQL queries
    logging: console.log
  }
);

const Video = sequelize.define('Video', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: DataTypes.TEXT,
  user_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  duration: DataTypes.INTEGER,
  views: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  likes: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  video_url: DataTypes.STRING,
  thumbnail_url: DataTypes.STRING,
  tags: DataTypes.ARRAY(DataTypes.STRING),
  category: DataTypes.STRING,
  status: {
    type: DataTypes.STRING,
    defaultValue: 'published'
  }
}, {
  tableName: 'videos',
  timestamps: true,
  underscored: true
});

module.exports = { Video, sequelize };
