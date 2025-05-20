import { Request, Response } from 'express';
import * as noteService from '../services/noteService';

export const getAllNotes = async (req: Request, res: Response) => {
  const page = parseInt(req.query._page as string) || 1;
  const perPage = parseInt(req.query._per_page as string) || 10;
  const { notes, count } = await noteService.getAllNotes(page, perPage);
  res.set('X-Total-Count', count.toString());
  res.status(200).json(notes);
};

export const getNoteById = async (req: Request, res: Response) => {
  const note = await noteService.getNoteById(req.params.id);
  if (!note) return res.status(404).json({ message: 'Note not found' });
  res.json(note);
};

export const createNote = async (req: Request, res: Response) => {
  const note = await noteService.createNote(req.body);
  res.status(201).json(note);
};

export const updateNoteById = async (req: Request, res: Response) => {
  const note = await noteService.updateNoteById(req.params.id, req.body);
  if (!note) return res.status(404).json({ message: 'Note not found' });
  res.json(note);
};

export const deleteNoteById = async (req: Request, res: Response) => {
  const deleted = await noteService.deleteNoteById(req.params.id);
  if (!deleted) return res.status(404).json({ message: 'Note not found' });
  res.status(204).end();
};

export const getNoteByIndex = async (req: Request, res: Response) => {
  const index = parseInt(req.params.i);
  const note = await noteService.getNoteByIndex(index);
  if (!note) return res.status(404).json({ message: 'Note not found' });
  res.json(note);
};

export const updateNoteByIndex = async (req: Request, res: Response) => {
  const index = parseInt(req.params.i);
  const note = await noteService.updateNoteByIndex(index, req.body);
  if (!note) return res.status(404).json({ message: 'Note not found' });
  res.json(note);
};

export const deleteNoteByIndex = async (req: Request, res: Response) => {
  const index = parseInt(req.params.i);
  const deleted = await noteService.deleteNoteByIndex(index);
  if (!deleted) return res.status(404).json({ message: 'Note not found' });
  res.status(204).end();
};