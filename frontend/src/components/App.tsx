import { useState } from "react";
import { useNotes } from "../contexts/NotesContext";
import "./App.css";

function App() {
  const { state, dispatch } = useNotes();
  const { notes, totalPages, currentPage, notification } = state;

  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState("");

  const handleDelete = async (id: string) => {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/notes/${id}`, {
      method: "DELETE",
    });
    dispatch({ type: "DELETE_NOTE", payload: id });
  };

  const handleSave = async (id: string) => {
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/notes/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: editedContent }),
    });
    const updated = await res.json();
    dispatch({ type: "UPDATE_NOTE", payload: updated });
    setEditingNoteId(null);
  };

  const handlePageChange = (page: number) => {
    dispatch({ type: "SET_PAGE", payload: page });
  };

  function getPageRange(activePage: number, totalPages: number): number[] {
    if (totalPages <= 5) return Array.from({ length: totalPages }, (_, i) => i + 1);
    if (activePage <= 3) return [1, 2, 3, 4, 5];
    if (activePage >= totalPages - 2)
      return Array.from({ length: 5 }, (_, i) => totalPages - 4 + i);
    return [activePage - 2, activePage - 1, activePage, activePage + 1, activePage + 2];
  }

  return (
    <>
      <div className="notification">{notification}</div>

      <div>
        {notes.map((note) => (
          <div key={note._id} className="note" data-testid={note._id}>
            <h2>{note.title}</h2>
            {note.author && <small>By {note.author.name}</small>}

            {editingNoteId === note._id ? (
              <>
                <textarea
                  data-testid={`text_input-${note._id}`}
                  name={`text_input-${note._id}`}
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                />
                <button
                  data-testid={`text_input_save-${note._id}`}
                  onClick={() => handleSave(note._id)}
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
                  data-testid={`edit-${note._id}`}
                  onClick={() => {
                    setEditingNoteId(note._id);
                    setEditedContent(note.content);
                  }}
                >
                  Edit
                </button>
              </>
            )}

            <button
              name={`delete-${note._id}`}
              onClick={() => handleDelete(note._id)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      <span>page: {currentPage} / {totalPages}</span>

      <div>
        <button name="first" onClick={() => handlePageChange(1)} disabled={currentPage === 1}>first</button>
        <button name="previous" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>previous</button>
        {getPageRange(currentPage, totalPages).map((page) => (
          <button
            key={page}
            name={`page-${page}`}
            className={page === currentPage ? "active" : "not-active"}
            onClick={() => handlePageChange(page)}
            disabled={page === currentPage}
          >
            {page}
          </button>
        ))}
        <button name="next" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>next</button>
        <button name="last" onClick={() => handlePageChange(totalPages)} disabled={currentPage === totalPages}>last</button>
      </div>
    </>
  );
}

export default App;
