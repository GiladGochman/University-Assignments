import { useState, useContext } from 'react';
import { useNotes } from '../contexts/NotesContext';
import AuthContext from '../contexts/AuthContext';
import axios from 'axios';

export default function NoteList() {
  const { state, dispatch } = useNotes();
  const { state: authState } = useContext(AuthContext);
  const loggedInUser = authState.user;

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');

  const notes = state.cache[state.currentPage] || [];
  const isValid = editTitle.trim() !== '' && editContent.trim() !== '';

  const startEdit = (note: any) => {
    setEditingId(note.id);
    setEditTitle(note.title || '');
    setEditContent(note.content || '');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditContent('');
  };

  const saveEdit = async (e: React.FormEvent, id: string) => {
    e.preventDefault();
    try {
      const updated = (
        await axios.put(`/notes/${id}`, {
          title: editTitle,
          content: editContent,
        })
      ).data;
      dispatch({ type: 'UPDATE_NOTE', payload: updated });
      setEditingId(null);
    } catch {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to update note' });
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`/notes/${id}`);
      const response = await axios.get(
        `/notes?_page=${state.currentPage}&_limit=10`
      );
      dispatch({
        type: 'DELETE_NOTE',
        payload: {
          notes: response.data.notes,
          total: response.data.total,
        },
      });
    } catch {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to delete note' });
    }
  };

  return (
    <div className="notes-grid" data-testid="notes-grid">
      {notes.map((note: any) => (
        <div className="note" data-testid={`note-${note.id}`} key={note.id}>
          {editingId === note.id ? (
            <form onSubmit={(e) => saveEdit(e, note.id)} data-testid={`edit-form-${note.id}`}>
              <input
                type="text"
                value={editTitle}
                placeholder="Title"
                onChange={(e) => setEditTitle(e.target.value)}
                data-testid={`text_input_title_${note.id}`}
              />
              <textarea
                value={editContent}
                placeholder="Content"
                onChange={(e) => setEditContent(e.target.value)}
                data-testid={`text_input_content_${note.id}`}
              />
              <button
                type="submit"
                disabled={!isValid}
                data-testid={`text_input_save_${note.id}`}
              >
                Save
              </button>
              <button
                type="button"
                onClick={cancelEdit}
                data-testid={`text_input_cancel_${note.id}`}
              >
                Cancel
              </button>
            </form>
          ) : (
            <>
              <h3 data-testid={`note_title_${note.id}`}>{note.title}</h3>
              <small data-testid={`note_author_${note.id}`}>
                By {note.author?.name} ({note.author?.email})
              </small>
              <p data-testid={`note_content_${note.id}`}>{note.content}</p>
              {(note.author?.email === loggedInUser?.email ||
                note.author?.name === loggedInUser?.name ||
                note.author?.username === loggedInUser?.username) && (
                <>
                  <button
                    data-testid={`edit_${note.id}`}
                    onClick={() => startEdit(note)}
                  >
                    Edit
                  </button>
                  <button
                    data-testid={`delete_${note.id}`}
                    onClick={() => handleDelete(note.id)}
                  >
                    Delete
                  </button>
                </>
              )}
            </>
          )}
        </div>
      ))}
    </div>
  );
}
