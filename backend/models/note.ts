import mongoose from "mongoose";

// Define the schema for a Note
const noteSchema = new mongoose.Schema({
  title: { type: String, required: true },
  content: String,
  created_at: { type: Date, default: Date.now },
});

const Note = mongoose.model("Note", noteSchema);
export default Note;
