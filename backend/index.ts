import express from "express";
import dotenv from "dotenv";
import connectDB from "./config/db";
import notesRouter from "./routes/notes";

dotenv.config();

const app = express();
app.use(express.json());

connectDB();

app.use("/api/notes", notesRouter); // the route to get notes in json format
app.listen(3001, () => {
  console.log("Server running on port 3001");
});
