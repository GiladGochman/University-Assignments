import dotenv from 'dotenv';
import app from './expressApp';
import { connectDB } from './config/db';

dotenv.config();

const PORT = process.env.PORT || 3001;

const start = async () => {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
};

start();
