import express from "express";
import { Note } from "../models/note";
import {
  getAll,
  getById,
  getByIndex,
  create,
  update,
  remove,
} from "../controllers/notesController";
const router = express.Router();

// GET a single page of 10 notes
router.get("/page/:page", async (req, res) => {
  // use: localhost:3001/notes/page/1
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
