import { Note } from "../types/Note";

interface NoteListProps {
  notes: Note[];
}

export default function NoteList({ notes }: NoteListProps) {
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
