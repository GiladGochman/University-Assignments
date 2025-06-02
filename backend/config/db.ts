import mongoose from "mongoose";
import dotenv from "dotenv";
import { dot } from "node:test/reporters";
dotenv.config();

const connectDB = async () => {
  try {
    // concat the mongo url:
    const mongoURI =
      "mongodb+srv://" +
      process.env.DB_USER +
      ":" +
      process.env.DB_PASS +
      "@" +
      process.env.DB_URL +
      process.env.DB_NAME +
      "?" +
      process.env.DB_OPTIONS;

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
