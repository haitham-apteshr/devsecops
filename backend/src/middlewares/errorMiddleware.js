const config = require('../config');

const errorHandler = (err, req, res, next) => {
  console.error(err.stack);
  res.status(err.statusCode || 500).json({
    success: false,
    error: err.message || 'Server Error',
    stack: config.enableVulnerabilities ? err.stack : undefined // INSECURE: Exposing stack trace
  });
};

module.exports = errorHandler;
