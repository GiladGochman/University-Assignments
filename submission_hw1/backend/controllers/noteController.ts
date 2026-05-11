import { Request, Response, NextFunction } from 'express';
import { Note } from '../models/noteModel';
import { AuthReq } from '../middlewares/auth';

export const getNotes = async (_: Request, res: Response, next: NextFunction) => {
  try {
    const page = Number(_.query.page) || 1;
    const limit = 10, skip = (page-1)*limit;
    const notes = await Note.find().skip(skip).limit(limit).sort('-createdAt');
    const total = await Note.countDocuments();
    res.json({ notes, total, page, pages: Math.ceil(total/limit) });
  } catch (err) { next(err); }
};

export const createNote = async (req: AuthReq, res: Response, next: NextFunction) => {
  try {
    const { title, content } = req.body;
    const note = new Note({ title, content,
      author: { name: req.user.name, email: req.user.email },
      user: req.user._id
    });
    res.status(201).json(await note.save());
  } catch (err) { next(err); }
};

export const updateNote = async (req: AuthReq, res: Response, next: NextFunction) => {
  try {
    const note = await Note.findById(req.params.id);
    if (!note) return res.status(404).end();
    if (note.user.toString() !== req.user._id.toString())
      return res.status(403).json({ error: 'forbidden' });
    note.title = req.body.title; note.content = req.body.content;
    res.json(await note.save());
  } catch (err) { next(err); }
};

export const deleteNote = async (req: AuthReq, res: Response, next: NextFunction) => {
  try {
    const note = await Note.findById(req.params.id);
    if (!note) return res.status(404).end();
    if (note.user.toString() !== req.user._id.toString())
      return res.status(403).json({ error: 'forbidden' });
    await Note.findByIdAndDelete(note._id);
    res.status(204).end();
  } catch (err) { next(err); }
};