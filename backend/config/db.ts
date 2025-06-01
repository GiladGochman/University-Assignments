import mongoose from "mongoose";
import dotenv from "dotenv";
import { dot } from "node:test/reporters";
dotenv.config();

const connectDB = async () => {
  try {
    console.log(dotenv.config());
    const mongoURI = process.env.DB_URL;
    if (!mongoURI) {
      throw new Error(
        "Database connection string (DB_URL) is not defined in environment variables"
      );
    }
    await mongoose.connect(mongoURI);

    console.log("MongoDB connected successfully");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    process.exit(1); // Exit the process if DB connection fails
  }
};

export default connectDB;
