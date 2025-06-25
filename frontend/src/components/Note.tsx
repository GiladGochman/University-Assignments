import { useContext, useState } from 'react';
import { useNotes } from '../contexts/NotesContext';
import AuthContext from '../contexts/AuthContext';
import { deleteNote, updateNote } from '../services/notes';

type NoteProps = {
  id: string;
  title: string;
  content: string;
  author: { name: string; email: string } | null;
};

export default function Note({ id, title, content, author }: NoteProps) {
  const { state, dispatch } = useNotes();
  const { state: authState } = useContext(AuthContext);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);
  const [editContent, setEditContent] = useState(content);

  const tokenObj = localStorage.getItem('user-token');
  const token = tokenObj ? JSON.parse(tokenObj).token : null;

  const loggedInUserEmail = authState.user?.email;
  const isOwner = author?.email === loggedInUserEmail;

  const handleDelete = async () => {
    if (!token) {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'User not authenticated' });
      return;
    }
    try {
      await deleteNote(id, token);
      const updatedNotes = (state.cache[state.currentPage] || []).filter(n => n.id !== id);
      dispatch({
        type: 'DELETE_NOTE',
        payload: {
          notes: updatedNotes,
          total: state.total - 1,
        },
      });
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Note deleted' });
    } catch {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to delete note' });
    }
  };

  const handleSave = async () => {
    if (!token) {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'User not authenticated' });
      return;
    }
    try {
      const updatedNote = await updateNote(id, { title: editTitle, content: editContent }, token);
      const updatedNotes = (state.cache[state.currentPage] || []).map(n =>
        n.id === id ? updatedNote : n
      );
      dispatch({
        type: 'UPDATE_NOTE',
        payload: updatedNote,
      });
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Note updated' });
      setIsEditing(false);
    } catch {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to update note' });
    }
  };

  return (
    <div className="note" data-testid={id}>
      {isEditing ? (
        <>
          <input
            type="text"
            value={editTitle}
            onChange={e => setEditTitle(e.target.value)}
            placeholder="Title"
            data-testid={`edit_title_input_${id}`}
          />
          <textarea
            value={editContent}
            onChange={e => setEditContent(e.target.value)}
            placeholder="Content"
            data-testid={`edit_content_input_${id}`}
          />
          <button onClick={handleSave} 
          disabled={!editTitle.trim() || !editContent.trim()}
          data-testid={`save_button_${id}`}
          >
            Save
          </button>
          <button 
          onClick={() => setIsEditing(false)}
          data-testid={`cancel_button_${id}`}
          >
            Cancel
          </button>
        </>
      ) : (
        <>
          <h2 data-testid={`note_title_${id}`}>{title}</h2>
          {author && (
            <small data-testid={`note_author_${id}`}>
              By {author.name} ({author.email})
            </small>
          )}
          <p data-testid={`note_content_${id}`}>{content}</p>
          {isOwner && (
            <>
              <button data-testid={`edit-${id}`} onClick={() => setIsEditing(true)}>
                Edit
              </button>
              <button data-testid={`delete-${id}`} onClick={handleDelete}>
                Delete
              </button>
            </>
          )}
        </>
      )}
    </div>
  );
}
