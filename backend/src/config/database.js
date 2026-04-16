const { Sequelize } = require('sequelize');
const config = require('./index');

const sequelize = new Sequelize(config.db.database, config.db.user, config.db.password, {
  host: config.db.host,
  port: config.db.port,
  dialect: 'mysql',
  logging: false, // Set to console.log to see SQL queries during development
});

module.exports = sequelize;
