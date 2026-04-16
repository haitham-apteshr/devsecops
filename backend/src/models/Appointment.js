const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const User = require('./User');
const Service = require('./Service');

const Appointment = sequelize.define('Appointment', {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  user_id: {
    type: DataTypes.INTEGER,
    references: {
      model: User,
      key: 'id'
    }
  },
  service_id: {
    type: DataTypes.INTEGER,
    references: {
      model: Service,
      key: 'id'
    }
  },
  appointment_date: {
    type: DataTypes.DATE,
    allowNull: false,
  },
  status: {
    type: DataTypes.STRING,
    defaultValue: 'Pending'
  }
}, {
  tableName: 'appointments',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

Appointment.belongsTo(User, { foreignKey: 'user_id', as: 'user' });
User.hasMany(Appointment, { foreignKey: 'user_id' });

Appointment.belongsTo(Service, { foreignKey: 'service_id', as: 'service' });
Service.hasMany(Appointment, { foreignKey: 'service_id' });

module.exports = Appointment;
