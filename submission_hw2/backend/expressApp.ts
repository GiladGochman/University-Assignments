import express from "express";
import dotenv from "dotenv";
import connectDB from "./config/db";
import notesRouter from "./routes/notes";
import testRouter from "./routes/testRouter";
import { logRequests } from "./middlewares/logRequests";
import cors from "cors";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
app.use(logRequests);

if (process.env.NODE_ENV !== "test") {
  // כי הייתה לי בעיה בהרצת טסטים
  connectDB();
}

app.use("/notes", notesRouter);
if (process.env.NODE_ENV === "dev") {
  app.use("/test", testRouter);
}

export default app;
