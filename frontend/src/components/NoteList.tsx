import { useNotes } from "../contexts/NotesContext";
import { useNoteCache } from "../hooks/useNoteCache";
import Note from "./Note";

export default function NoteList() {
  const { state } = useNotes();
  const currentPage = state.currentPage;

  const notes = useNoteCache(currentPage);

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
