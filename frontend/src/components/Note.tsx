import { useState } from 'react';
import { useNotes } from '../contexts/NotesContext';

type NoteProps = {
  _id: string;
  title: string;
  content: string;
  author: { name: string; email: string } | null;
};

export default function Note({ _id, title, content, author }: NoteProps) {
  const { dispatch } = useNotes();
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content);

  const handleDelete = async () => {
    await fetch(`${import.meta.env.VITE_BACKEND_URL}/notes/${_id}`, {
      method: 'DELETE',
    });
    dispatch({ type: 'DELETE_NOTE', payload: _id });
    dispatch({ type: "SET_NOTIFICATION", payload: 'Note deleted' });
  };

  const handleSave = async () => {
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/notes/${_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, author, content: editedContent }),
    });
    const updated = await res.json();
    dispatch({ type: 'UPDATE_NOTE', payload: updated });
    dispatch({ type: "SET_NOTIFICATION" , payload: 'Note updated' });
    setIsEditing(false);
  };

  return (
    <div className="note" data-testid={_id}>
      <h2>{title}</h2>
      {author && <small>By {author.name}</small>}

      {isEditing ? (
        <>
          <textarea
            data-testid={`text_input-${_id}`}
            name={`text_input-${_id}`}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
          />
          <button data-testid={`text_input_save-${_id}`} onClick={handleSave}>
            Save
          </button>
          <button data-testid={`text_input_cancel-${_id}`} onClick={() => setIsEditing(false)}>
            Cancel
          </button>
        </>
      ) : (
        <>
          <p>{content}</p>
          <button data-testid={`edit-${_id}`} onClick={() => setIsEditing(true)}>
            Edit
          </button>
        </>
      )}

      <button data-testid={`delete-${_id}`} name={`delete-${_id}`} onClick={handleDelete}>
        Delete
      </button>
    </div>
  );
}
