import { Note } from "../types/Note";
import { useNotesContext } from "../contexts/NotesContext";

export default function NoteList() {
  const { state } = useNotesContext();
  const { notes } = state;

  return (
    <div>
      {notes.map((note) => (
        <div key={note._id} className="note" id={note._id.toString()}>
          <h2>{note.title}</h2>
          <small>By {note.author.name}</small>
          <br />
          {note.content}
        </div>
      ))}
    </div>
  );
}
