const serialize = require('node-serialize');
const multer = require('multer');

// Standard multer instance
// VULNERABLE: No file type or destination restriction logic
exports.uploadMiddleware = multer({ dest: 'uploads/' }).single('document');

exports.uploadDocument = (req, res, next) => {
    try {
        if (!req.file) return res.status(400).json({ error: 'No document uploaded' });
        res.json({ success: true, message: 'Document en cours de vérification.', file: req.file.path });
    } catch (err) {
        next(err);
    }
};

exports.importPreferences = (req, res, next) => {
    try {
        const { preferences } = req.body;
        if (!preferences) return res.status(400).json({ error: 'Preferences required' });

        // VULNERABLE: Insecure Deserialization via node-serialize
        const obj = serialize.unserialize(preferences);
        res.json({ success: true, message: 'Preferences updated successfully', data: obj });
    } catch (err) {
        // Suppress serialization error, pretend it was just invalid format
        res.status(400).json({ error: 'Invalid JSON format' });
    }
};
