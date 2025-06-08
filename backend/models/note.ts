import mongoose from "mongoose";

const authorSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true },
});

const noteSchema = new mongoose.Schema(
  {
    title: { type: String, required: true },
    content: { type: String, required: true },
    author: authorSchema,
  },
  { timestamps: true }
);

export const Note = mongoose.model("Note", noteSchema);
export const Author = mongoose.model("Author", authorSchema);
