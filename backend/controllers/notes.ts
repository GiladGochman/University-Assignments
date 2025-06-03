import { Request, Response } from "express";
import Note from "../models/note";
import mongoose from "mongoose";

// GET /notes?_page=1&_per_page=10
export async function getNotesByPage(req: Request, res: Response) {
  const page = parseInt(req.query._page as string) || 1;
  const perPage = parseInt(req.query._per_page as string) || 10;

  try {
    const notes = await Note.find()
      .skip((page - 1) * perPage)
      .limit(perPage);
    res.status(200).json(notes);
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
}

// GET /notes/:id
export async function getNoteById(req: Request, res: Response) {
  const { id } = req.params;
  if (!mongoose.isValidObjectId(id))
    return res.status(404).json({ error: "Note not found" });

  try {
    const note = await Note.findById(id);
    if (!note) return res.status(404).json({ error: "Note not found" });
    res.status(200).json(note);
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
}

// POST /notes
export async function createNote(req: Request, res: Response) {
  try {
    const note = new Note(req.body);
    await note.validate(); // trigger validation error if invalid
    await note.save();
    res.status(201).json(note);
  } catch (err: any) {
    if (err.name === "ValidationError") {
      res.status(400).json({ error: "Bad Request", details: err.message });
    } else {
      res.status(500).json({ error: "Internal Server Error" });
    }
  }
}

// PUT /notes/:id
export async function updateNoteById(req: Request, res: Response) {
  const { id } = req.params;
  if (!mongoose.isValidObjectId(id))
    return res.status(404).json({ error: "Note not found" });

  try {
    const updated = await Note.findByIdAndUpdate(id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!updated) return res.status(404).json({ error: "Note not found" });
    res.status(200).json(updated);
  } catch (err: any) {
    if (err.name === "ValidationError") {
      res.status(400).json({ error: "Bad Request", details: err.message });
    } else {
      res.status(500).json({ error: "Internal Server Error" });
    }
  }
}

// DELETE /notes/:id
export async function deleteNoteById(req: Request, res: Response) {
  const { id } = req.params;
  if (!mongoose.isValidObjectId(id))
    return res.status(404).json({ error: "Note not found" });

  try {
    const result = await Note.findByIdAndDelete(id);
    if (!result) return res.status(404).json({ error: "Note not found" });
    res.sendStatus(204);
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
}

// GET /notes/by-index/:i
export async function getNoteByIndex(req: Request, res: Response) {
  const i = parseInt(req.params.i);
  if (isNaN(i) || i < 0)
    return res.status(404).json({ error: "Invalid index" });

  try {
    const note = await Note.findOne().skip(i);
    if (!note) return res.status(404).json({ error: "Note not found" });
    res.status(200).json(note);
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
}

// PUT /notes/by-index/:i
export async function updateNoteByIndex(req: Request, res: Response) {
  const i = parseInt(req.params.i);
  if (isNaN(i) || i < 0)
    return res.status(404).json({ error: "Invalid index" });

  try {
    const note = await Note.findOne().skip(i);
    if (!note) return res.status(404).json({ error: "Note not found" });

    Object.assign(note, req.body);
    await note.validate();
    await note.save();
    res.status(200).json(note);
  } catch (err: any) {
    if (err.name === "ValidationError") {
      res.status(400).json({ error: "Bad Request", details: err.message });
    } else {
      res.status(500).json({ error: "Internal Server Error" });
    }
  }
}

// DELETE /notes/by-index/:i
export async function deleteNoteByIndex(req: Request, res: Response) {
  const i = parseInt(req.params.i);
  if (isNaN(i) || i < 0)
    return res.status(404).json({ error: "Invalid index" });

  try {
    const note = await Note.findOne().skip(i);
    if (!note) return res.status(404).json({ error: "Note not found" });

    await Note.findByIdAndDelete(note._id);
    res.sendStatus(204);
  } catch (err) {
    res.status(500).json({ error: "Internal Server Error" });
  }
}
