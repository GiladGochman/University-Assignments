import express from "express";
import Note from "../models/note";

const router = express.Router();

router.get("/test", async (req, res) => {
  // use: localhost:3000/api/notes/test

  const note = new Note({
    title: "Test Note",
    content: "This is a test note.",
  });

  await note.save();
  console.log("Test note created:", note);
  const notes = await Note.find();
  //   res.json(notes);
});

// GET all notes with pagination
router.get("/", async (req, res) => {
  // use: localhost:3000/api/notes
  const page = parseInt(req.query._page as string) || 1;
  const limit = parseInt(req.query._limit as string) || 10;
  const skip = (page - 1) * limit;

  try {
    const notes = await Note.find().skip(skip).limit(limit);
    const totalNotes = await Note.countDocuments();
    res.set("X-Total-Count", totalNotes.toString());
    res.json(notes);
  } catch (error) {
    console.error("Error fetching notes:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

export default router;
