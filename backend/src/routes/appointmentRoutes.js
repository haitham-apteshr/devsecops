const express = require('express');
const { getAppointments, createAppointment, getServices, getAppointmentById, searchAppointments, cancelAppointment } = require('../controllers/appointmentController');
const { protect } = require('../middlewares/authMiddleware');

const router = express.Router();

router.get('/meta/services', getServices);

// Protected routes below
router.use(protect);
router.get('/search', searchAppointments);
router.get('/:id', getAppointmentById);
router.delete('/:id', cancelAppointment);
router.get('/', getAppointments);
router.post('/', createAppointment);

module.exports = router;
