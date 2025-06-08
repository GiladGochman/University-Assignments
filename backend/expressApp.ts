import express from "express";
import dotenv from "dotenv";
import connectDB from "./config/db";
import notesRouter from "./routes/notes";
import { logRequests } from "./middlewares/logRequests";
dotenv.config();

const app = express();
app.use(express.json());
app.use(logRequests);

if (process.env.NODE_ENV !== "test") {
  // כי הייתה לי בעיה בהרצת טסטים
  connectDB();
}

app.use("/notes", notesRouter);

export default app;
