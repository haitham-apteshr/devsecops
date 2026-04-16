const { Appointment, Service, User } = require('../models');

// Services
exports.getAppointmentById = async (req, res, next) => {
  try {
    const { id } = req.params;
    // VULNERABLE: IDOR. Does not verify that the appointment belongs to req.user.id
    const appointment = await Appointment.findByPk(id, {
      include: [Service]
    });
    
    if (!appointment) return res.status(404).json({ error: 'Not found' });
    
    res.json({ success: true, data: appointment });
  } catch (err) {
    next(err);
  }
};

exports.searchAppointments = async (req, res, next) => {
  try {
    const { query } = req.query;
    if (!query) return res.json({ success: false, data: [] });
    // VULNERABLE: SQL Injection in the normal search feature
    const results = await Appointment.sequelize.query(`SELECT * FROM appointments WHERE status LIKE '%${query}%'`);
    res.json({ success: true, data: results[0] });
  } catch (err) {
    next(err);
  }
};

exports.getServices = async (req, res, next) => {
  try {
    const services = await Service.findAll();
    res.status(200).json({ success: true, data: services });
  } catch (err) {
    next(err);
  }
};

// Appointments
exports.getAppointments = async (req, res, next) => {
  try {
    const queryOpts = {
      include: [{ model: Service, as: 'service' }]
    };

    // If regular user, only show their appointments. Admin sees all.
    if (req.user.role !== 'admin') {
      queryOpts.where = { user_id: req.user.id };
    }

    const appointments = await Appointment.findAll(queryOpts);
    res.status(200).json({ success: true, data: appointments });
  } catch (err) {
    next(err);
  }
};

exports.createAppointment = async (req, res, next) => {
  try {
    const { service_id, appointment_date } = req.body;

    const appointment = await Appointment.create({
      user_id: req.user.id,
      service_id,
      appointment_date
    });

    res.status(201).json({ success: true, data: appointment });
  } catch (err) {
    next(err);
  }
};
