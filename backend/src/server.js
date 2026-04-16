const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const config = require('./config');
const { sequelize } = require('./models');
const errorHandler = require('./middlewares/errorMiddleware');

const app = express();

// Security middlewares (Helmet disabled locally for some testing, but good practice)
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/appointments', require('./routes/appointmentRoutes'));
app.use('/api/user', require('./routes/userRoutes'));
app.use('/api/contact', require('./routes/contactRoutes'));

app.use(errorHandler);

const PORT = config.port;

sequelize.sync({ force: false }).then(() => {
  console.log('Database connected successfully.');
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}).catch(err => {
  console.error('Database connection failed:', err);
});
