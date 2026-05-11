import mongoose from "mongoose";

const authorSchema = new mongoose.Schema({
  name: { type: String, default: "Anonymous" },
  email: { type: String, default: "" },
});

const noteSchema = new mongoose.Schema(
  {
    title: { type: String, default: "" },
    content: { type: String, required: true },
    author: authorSchema,
  },
  { timestamps: true }
);

export const Note = mongoose.model("Note", noteSchema);
export const Author = mongoose.model("Author", authorSchema);
