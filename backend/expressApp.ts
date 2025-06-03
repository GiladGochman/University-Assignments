import express from "express";
import dotenv from "dotenv";
import connectDB from "./config/db";
import notesRouter from "./routes/notes";
// import logRequests from "./middlewares/logRequests";

dotenv.config();

const app = express();
app.use(express.json());
// app.use(logRequests);
connectDB();

app.use("/api/notes", notesRouter);

export default app;
