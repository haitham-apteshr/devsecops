const express = require('express');
const { checkServerStatus, searchFaq, getFaqDocument } = require('../controllers/contactController');

const router = express.Router();

router.get('/faq', searchFaq);
router.post('/status', checkServerStatus);
router.get('/download', getFaqDocument);

module.exports = router;
