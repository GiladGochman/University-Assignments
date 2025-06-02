import mongoose from "mongoose";

// Define the schema for a Note
const authorSchema = new mongoose.Schema(
  {
    name: { type: String, required: true },
    email: { type: String, required: true },
  },
  { _id: false }
); // prevent creation of nested _id for subdocument

const noteSchema = new mongoose.Schema({
  title: { type: String, required: true },
  author: {
    type: authorSchema,
    required: false, // allows null
    default: null,
  },
  content: { type: String, required: true },
});

const Note = mongoose.model("Note", noteSchema);
export default Note;
