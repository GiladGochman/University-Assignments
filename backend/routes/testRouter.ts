import express from 'express';
import { Note } from '../models/noteModel';
import { User } from '../models/User';

const router = express.Router();

router.delete('/reset', async (_req, res) => {
  await Note.deleteMany({});
  await User.deleteMany({});
  res.status(204).end();
});

router.post('/notes', async (req, res) => {
  const note = await Note.create(req.body);
  res.status(201).json(note);
});

export default router;