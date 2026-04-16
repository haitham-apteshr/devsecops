const express = require('express');
const { uploadMiddleware, uploadDocument, importPreferences } = require('../controllers/userController');
const { protect } = require('../middlewares/authMiddleware');

const router = express.Router();

router.use(protect);
router.post('/upload', uploadMiddleware, uploadDocument);
router.post('/preferences', importPreferences);

module.exports = router;
