// src/components/EditData.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { useNotesContext } from "../contexts/NotesContext";

const EditData = () => {
  const { state, dispatch, notification, setNotification } = useNotesContext();
  const { notes } = state;

  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState("");
  const [newNoteText, setNewNoteText] = useState("");
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    axios.get("http://localhost:3001/notes?page=1").then((res) => {
      if (Array.isArray(res.data)) {
        dispatch({ type: "SET_NOTES", payload: res.data });
      } else {
        console.error("Expected array from API, got:", res.data);
        dispatch({ type: "SET_NOTES", payload: [] });
      }
    });
  }, [dispatch]);

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

  const handleAddNote = async () => {
    const res = await axios.post("http://localhost:3001/notes", {
      content: newNoteText,
    });
    dispatch({ type: "ADD_NOTE", payload: res.data });
    setNewNoteText("");
    setAdding(false);
    setNotification("Added a new note");
  };

  return (
    <div>
      {notification && <div className="notification">{notification}</div>}

      {adding ? (
        <div>
          <input
            type="text"
            value={newNoteText}
            onChange={(e) => setNewNoteText(e.target.value)}
            name="text_input_new_note"
            data-testid="text_input_new_note"
          />
          <button name="text_input_save_new_note" onClick={handleAddNote}>
            Save
          </button>
          <button
            name="text_input_cancel_new_note"
            onClick={() => {
              setAdding(false);
              setNewNoteText("");
            }}
          >
            Cancel
          </button>
        </div>
      ) : (
        <button name="add_new_note" onClick={() => setAdding(true)}>
          Add Note
        </button>
      )}

      {/* רשימת פתקים - רק אם notes הוא מערך */}
      {Array.isArray(notes) &&
        notes.map((note) => (
          <div key={note._id} className="note" data-testid={note._id}>
            <h2>new note</h2>
            <small>By {note.author?.name ?? "Unknown"}</small>

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
                {note.content}
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
};

export default EditData;
