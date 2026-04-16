const sequelize = require('../config/database');
const Role = require('./Role');
const User = require('./User');
const Service = require('./Service');
const Appointment = require('./Appointment');

module.exports = {
  sequelize,
  Role,
  User,
  Service,
  Appointment
};
