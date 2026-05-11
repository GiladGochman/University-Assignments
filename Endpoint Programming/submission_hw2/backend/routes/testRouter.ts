import express from "express";
import { Note } from "../models/note";
import { Router, Request, Response } from "express";

const router = express.Router();

router.get("/", (req: Request, res: Response) => {
  res.json({ message: "Test route is working!" });
});
// Delete all notes - development only
router.delete("/reset", async (_req, res) => {
  try {
    await Note.deleteMany({});
    res.status(204).end();
  } catch (error) {
    res.status(500).json({ error: "Failed to delete notes" });
  }
});

export default router;
