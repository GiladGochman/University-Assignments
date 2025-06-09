import { Request, Response } from "express";
import * as notesService from "../services/notesServices";

export const getAll = async (_req: Request, res: Response) => {
  const notes = await notesService.getAllNotes();
  res.json(notes);
};

export async function getNotesByIndex(req: Request, res: Response) {
  const index = parseInt(req.params.i);
  if (isNaN(index) || index < 0) {
    return res.status(400).json({ error: "Invalid index" });
  }

  const notes = await notesService.getNotesByIndex(index);
  res.json(notes);
}

export const getById = async (req: Request, res: Response) => {
  const note = await notesService.getNoteById(req.params.id);
  if (!note) return res.status(404).json({ error: "Note not found" });
  res.json(note);
};

export const getByIndex = async (req: Request, res: Response) => {
  const index = parseInt(req.params.i);
  if (isNaN(index)) return res.status(400).json({ error: "Invalid index" });

  const note = await notesService.getNoteByIndex(index);
  if (!note) return res.status(404).json({ error: "Note not found at index" });
  res.json(note);
};

export const create = async (req: Request, res: Response) => {
  const { title, content } = req.body;
  if (!title || !content)
    return res.status(400).json({ error: "Missing fields" });

  const note = await notesService.createNote({
    title,
    content,
    author: req.body.author || null,
  });
  res.status(201).json(note);
};

export const update = async (req: Request, res: Response) => {
  const note = await notesService.updateNote(req.params.id, req.body);
  if (!note)
    return res.status(404).json({ error: "Note not found or invalid ID" });
  res.json(note);
};

export const remove = async (req: Request, res: Response) => {
  const note = await notesService.deleteNote(req.params.id);
  if (!note)
    return res.status(404).json({ error: "Note not found or invalid ID" });
  res.status(204).end();
};
