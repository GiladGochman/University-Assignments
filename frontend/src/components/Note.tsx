/* eslint-disable @typescript-eslint/no-unused-vars */
import { useState } from 'react';
import { useNotes } from '../contexts/NotesContext';
import { deleteNote, updateNote } from '../services/notes';

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

  const token = localStorage.getItem('user-token');

  const handleDelete = async () => {
    try {
      await deleteNote(_id, token!);
      dispatch({ type: 'DELETE_NOTE', payload: _id });
      dispatch({ type: "SET_NOTIFICATION", payload: 'Note deleted' });
    } catch (error) {
      dispatch({ type: "SET_NOTIFICATION", payload: 'Failed to delete note' });
    }
  };

  const handleSave = async () => {
    try {
      const updated = await updateNote(_id, { title, content: editedContent }, token!);
      dispatch({ type: 'UPDATE_NOTE', payload: updated });
      dispatch({ type: "SET_NOTIFICATION", payload: 'Note updated' });
      setIsEditing(false);
    } catch (error) {
      dispatch({ type: "SET_NOTIFICATION", payload: 'Failed to update note' });
    }
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
