import mongoose from 'mongoose';

const noteSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
  },
  author: {
    type: {
      name: { type: String, required: true },
      email: { type: String, required: true }
    },
    required: false,
    default: null,
  },
  content: {
    type: String,
    required: true,
  },
});

const Note = mongoose.model('Note', noteSchema, 'notes');
export default Note;
