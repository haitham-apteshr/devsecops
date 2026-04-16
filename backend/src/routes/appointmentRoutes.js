const express = require('express');
const { getAppointments, createAppointment, getServices, getAppointmentById, searchAppointments } = require('../controllers/appointmentController');
const { protect } = require('../middlewares/authMiddleware');

const router = express.Router();

router.get('/services', getServices);

// Protected routes below
router.use(protect);
router.get('/search', searchAppointments); // Must be before /:id
router.get('/:id', getAppointmentById);
router.get('/', getAppointments);
router.post('/', createAppointment);

module.exports = router;
