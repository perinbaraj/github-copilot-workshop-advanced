const { Sequelize, DataTypes } = require('sequelize');
const { sequelize } = require('./Video');

const View = sequelize.define('View', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  video_id: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  user_id: {
    type: DataTypes.INTEGER,
    allowNull: true
  },
  watch_duration: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },
  ip_address: DataTypes.STRING,
  user_agent: DataTypes.TEXT
}, {
  tableName: 'views',
  timestamps: true,
  underscored: true,
  // PERFORMANCE ISSUE: No indexes defined
});

module.exports = View;
