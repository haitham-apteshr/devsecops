const jwt = require('jsonwebtoken');
const config = require('../config');

exports.protect = (req, res, next) => {
  let token;

  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (!token) {
    return res.status(401).json({ success: false, error: 'Not authorized to access this route' });
  }

  try {
    let decoded;
    if (config.enableVulnerabilities) {
      // INSECURE: Uses simple decode without signature verification if vulnerabilities enabled,
      // simulating algorithmic confusion or accepting 'none' algorithms.
      decoded = jwt.decode(token);
    } else {
      decoded = jwt.verify(token, config.jwtSecret);
    }
    req.user = decoded; // { id, role }
    next();
  } catch (err) {
    return res.status(401).json({ success: false, error: 'Token is invalid or expired' });
  }
};

exports.authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ success: false, error: `User role ${req.user ? req.user.role : 'none'} is not authorized to access this route` });
    }
    next();
  };
};
