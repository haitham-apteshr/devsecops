require('dotenv').config();

module.exports = {
  port: process.env.PORT || 5000,
  jwtSecret: process.env.JWT_SECRET || 'supersecretjwtkey',
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    user: process.env.DB_USER || 'devsecops_user',
    password: process.env.DB_PASSWORD || 'securepassword',
    database: process.env.DB_NAME || 'devsecops_db',
  },
  enableVulnerabilities: process.env.ENABLE_VULNERABILITIES === 'true'
};
