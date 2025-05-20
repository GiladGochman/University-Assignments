import express from 'express';
import Note from '../models/noteModel';

const router = express.Router();

router.delete('/reset', async (_req, res) => {
  await Note.deleteMany({});
  res.status(204).end();
});

export default router;
