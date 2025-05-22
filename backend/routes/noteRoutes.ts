import express from 'express';
import * as noteController from '../controllers/noteController';

const router = express.Router();

router.get('/by-index/:i', noteController.getNoteByIndex);      // GET /notes/by-index/:i
router.put('/by-index/:i', noteController.updateNoteByIndex);   // PUT /notes/by-index/:i
router.delete('/by-index/:i', noteController.deleteNoteByIndex);// DELETE /notes/by-index/:i

router.get('/', noteController.getAllNotes);                    // GET /notes?_page=&_per_page=
router.get('/:id', noteController.getNoteById);                 // GET /notes/:id
router.post('/', noteController.createNote);                    // POST /notes
router.put('/:id', noteController.updateNoteById);              // PUT /notes/:id
router.delete('/:id', noteController.deleteNoteById);           // DELETE /notes/:id

export default router;
