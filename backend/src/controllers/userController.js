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

exports.getUserProfile = async (req, res, next) => {
    try {
        const user = await User.findByPk(req.user.id);
        // VULNERABLE: Sensitive Data Exposure. Returning the entire user object including password_hash.
        res.json({ success: true, data: user });
    } catch (err) {
        next(err);
    }
};

exports.importPreferences = (req, res, next) => {
    try {
        const { preferences } = req.body;
        if (!preferences) return res.status(400).json({ error: 'Preferences required' });

        // VULNERABLE: Insecure Deserialization via node-serialize (Leading to RCE)
        // Attack payload: {"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('whoami', function(error, stdout, stderr) { console.log(stdout) });}()"}
        const obj = serialize.unserialize(preferences);
        res.json({ success: true, message: 'Preferences updated successfully', data: obj });
    } catch (err) {
        res.status(400).json({ error: 'Invalid preferences format' });
    }
};
