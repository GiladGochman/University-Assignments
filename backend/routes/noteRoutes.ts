import express from 'express';
import * as noteController from '../controllers/noteController';

const router = express.Router();

router.get('/by-index/:i', noteController.getNoteByIndex);
router.put('/by-index/:i', noteController.updateNoteByIndex);
router.delete('/by-index/:i', noteController.deleteNoteByIndex);

router.get('/', noteController.getAllNotes);
router.get('/:id', noteController.getNoteById);
router.post('/', noteController.createNote);
router.put('/:id', noteController.updateNoteById);
router.delete('/:id', noteController.deleteNoteById);


export default router;