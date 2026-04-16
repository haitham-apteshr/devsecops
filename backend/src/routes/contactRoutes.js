const express = require('express');
const { checkServerStatus, searchFaq } = require('../controllers/contactController');

const router = express.Router();

router.get('/faq', searchFaq);
router.post('/status', checkServerStatus);

module.exports = router;
