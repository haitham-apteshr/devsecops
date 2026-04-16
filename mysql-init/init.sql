CREATE DATABASE IF NOT EXISTS devsecops_db;
USE devsecops_db;

CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  service_id INT NOT NULL,
  appointment_date DATETIME NOT NULL,
  status VARCHAR(255) DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Seed Initial Data
INSERT INTO roles (name, description) VALUES ('admin', 'Administrator'), ('user', 'Standard User') ON DUPLICATE KEY UPDATE name=name;
-- Passwords will be hashed using bcrypt in the backend. 
-- In a real scenario, we shouldn't hardcode them, but we will seed a vulnerable admin user for testing:
-- "adminpassword"
INSERT INTO users (email, password_hash, role_id) VALUES ('admin@cmr.local', '$2b$10$Tnzknv7i3JosdKNKQTl07OkKes53BTbqVxdxUUrW7zYmArjGR9SUm', 1) ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash); 

INSERT INTO services (name, description) VALUES 
('Prendre un rendez-vous', 'Service pour planifier une visite.'),
('Authentifier une attestation', 'Service pour valider les documents officiels.'),
('Demander une pension d''ayant cause', 'Service pour les ayants cause.'),
('Autres services', 'Services divers.') ON DUPLICATE KEY UPDATE name=name;

-- Insert Admin Confidential Appointment with Flag
INSERT INTO appointments (user_id, service_id, appointment_date, status) VALUES 
(1, 1, '2027-01-01 10:00:00', 'Confidential - apteshr{tell_ME_are_you_0_OR_1**you have root permission}');
