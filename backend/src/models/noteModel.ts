import mongoose from 'mongoose';

const noteSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
  },
  author: {
    type: {
      name: String,
      email: String,
    },
    required: false,
    default: null,
  },
  content: {
    type: String,
    required: true,
  },
});

const Note = mongoose.model('Note', noteSchema);
export default Note;
