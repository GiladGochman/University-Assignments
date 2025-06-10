import { useNotesContext } from "../contexts/NotesContext";
import { useState } from "react";
import axios from "axios";
// import { setNotification } from "../utils/notificationUtils";
import { Note } from "../types/Note";
// import { handleDelete, handleEdit } from "../utils/noteUtils";

export default function NoteList() {
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState("");
  const { state, dispatch, notification, setNotification } = useNotesContext();
  const { notes } = state;

  // services
  const handleDelete = async (id: string) => {
    await axios.delete(`http://localhost:3001/notes/${id}`);
    dispatch({ type: "DELETE_NOTE", payload: id });
    setNotification("Note deleted");
  };

  const handleEdit = (note: { _id: string; content: string }) => {
    setEditingNoteId(note._id);
    setEditingText(note.content);
  };

  const handleSaveEdit = async (id: string) => {
    const updatedNote = { content: editingText };
    const res = await axios.put(
      `http://localhost:3001/notes/${id}`,
      updatedNote
    );
    dispatch({ type: "UPDATE_NOTE", payload: res.data });
    setEditingNoteId(null);
    setNotification("Note updated");
  };
  return (
    <div>
      {notes.map((note) => (
        <div key={note._id} className="note" id={note._id.toString()}>
          <h2>{note.title}</h2>
          <small>By {note.author.name}</small>
          <br />
          {note.content}
          {editingNoteId === note._id ? (
            <>
              <textarea
                value={editingText}
                onChange={(e) => setEditingText(e.target.value)}
                data-testid={`text_input-${note._id}`}
                name={`text_input-${note._id}`}
              />
              <button
                data-testid={`text_input_save-${note._id}`}
                onClick={() => handleSaveEdit(note._id)}
              >
                Save
              </button>
              <button
                data-testid={`text_input_cancel-${note._id}`}
                onClick={() => setEditingNoteId(null)}
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <p>{note.content}</p>
              <button
                data-testid={`delete-${note._id}`}
                name={`delete-${note._id}`}
                onClick={() => handleDelete(note._id)}
              >
                Delete
              </button>
              <button
                data-testid={`edit-${note._id}`}
                onClick={() => handleEdit(note)}
              >
                Edit
              </button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
