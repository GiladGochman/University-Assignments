import express from "express";
import { Note } from "../models/note";
import {
  getAll,
  getById,
  getByIndex,
  create,
  update,
  remove,
  getNotesByIndex,
} from "../controllers/notesController";
const router = express.Router();

// router.get("/test", async (req, res) => {
//   // use: localhost:3000/api/notes/test

//   const note = new Note({
//     title: "Test Note",
//     content: "This is a test note.",
//   });

//   await note.save();
//   console.log("Test note created:", note);
//   const notes = await Note.find();
//   //   res.json(notes);
// });

// GET all notes with pagination
// router.get("/", async (req, res) => {
//   // use: localhost:3001/api/notes
//   // find the number of notes in the database
//   try {
//     const notes = await Note.find().skip(0).limit(Number.MAX_SAFE_INTEGER);
//     const totalNotes = await Note.countDocuments();
//     res.set("X-Total-Count", totalNotes.toString());
//     res.json(notes);
//   } catch (error) {
//     console.error("Error fetching notes:", error);
//     res.status(500).json({ message: "Internal server error" });
//   }
// });

// GET a single page of 10 notes
router.get("/page/:page", async (req, res) => {
  // use: localhost:3001/api/notes/page/1
  const page = parseInt(req.params.page) || 1;
  const limit = 10; // Fixed limit of 10 notes per page
  const skip = (page - 1) * limit;
  console.log("Fetching page:", page, "with limit:", limit);
  try {
    const notes = await Note.find().skip(skip).limit(limit);
    res.json(notes);
  } catch (error) {
    console.error("Error fetching notes:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});
router.get("/", getAll);
router.get("/:id", getById);
router.get("/by-index/:i", getByIndex);
router.post("/", create);
router.put("/:id", update);
router.delete("/:id", remove);

export default router;
