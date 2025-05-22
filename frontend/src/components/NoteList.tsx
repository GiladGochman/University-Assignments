import { useNotes } from '../contexts/NotesContext';
import Note from './Note';

export default function NoteList() {
  const { state } = useNotes();
  const { notes } = state;

  return (
    <div>
      {notes.map((note) => (
        <Note
          key={note._id}
          _id={note._id}
          title={note.title}
          content={note.content}
          author={note.author}
        />
      ))}
    </div>
  );
}
