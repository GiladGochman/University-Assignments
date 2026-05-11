import dotenv from 'dotenv';
dotenv.config();
export const { MONGODB_CONNECTION_URL, JWT_SECRET, PORT} = process.env;

