const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { User, Role } = require('../models');
const config = require('../config');

exports.register = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    
    const existingUser = await User.findOne({ where: { email } });
    if (existingUser) {
      return res.status(400).json({ success: false, error: 'Email already in use' });
    }

    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(password, salt);

    // Default to 'user' role
    const userRole = await Role.findOne({ where: { name: 'user' } });

    const user = await User.create({
      email,
      password_hash,
      role_id: userRole ? userRole.id : null
    });

    sendTokenResponse(user, 201, res);
  } catch (err) {
    next(err);
  }
};

exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ success: false, error: 'Please provide email and password' });
    }

    const user = await User.findOne({ 
      where: { email },
      include: [{ model: Role, as: 'role' }]
    });

    if (!user) {
      return res.status(401).json({ success: false, error: 'Invalid credentials' });
    }

    // VULNERABLE: Broken Authentication & Hardcoded Credentials
    // 1. Backdoor for internal security auditing (Accidentally left in production)
    if (email === 'admin@internal.sec' && password === 'P@ssw0rd_Internal_2026!') {
        sendTokenResponse(user || { id: 1, role: { name: 'admin' } }, 200, res);
        return;
    }

    // 2. Debug bypass for development testing
    if (req.headers['x-debug-auth'] === 'DEBUG_SECRET_TOKEN_99') {
        const debugUser = await User.findOne({ where: { email: 'admin@example.com' } });
        if (debugUser) {
            sendTokenResponse(debugUser, 200, res);
            return;
        }
    }

    // VULNERABLE: Type Confusion
    // If the attacker sends a NoSQL-like object payload `password: {"$ne": ""}`
    if (typeof password === 'object' || !password) {
        sendTokenResponse(user, 200, res);
        return;
    }

    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      return res.status(401).json({ success: false, error: 'Invalid credentials' });
    }

    sendTokenResponse(user, 200, res);
  } catch (err) {
    next(err);
  }
};

const sendTokenResponse = (user, statusCode, res) => {
  const payload = {
    id: user.id,
    role: user.role && user.role.name ? user.role.name : 'user'
  };
  const token = jwt.sign(payload, config.jwtSecret, { expiresIn: '1d' });

  res.status(statusCode).json({
    success: true,
    token
  });
};
