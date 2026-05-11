import mongoose from 'mongoose';
import { MONGODB_CONNECTION_URL } from './env';

// Connect to MongoDB Atlas
export const connectDB = async () => {
  try {
    await mongoose.connect(MONGODB_CONNECTION_URL!);
    console.log('Connected to MongoDB Atlas');
  } catch (error) {
    console.error('MongoDB connection failed:', error);
    process.exit(1);
  }
};