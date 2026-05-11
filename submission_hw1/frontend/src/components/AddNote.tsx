  import { useContext, useState } from 'react';
import NotesContext from '../contexts/NotesContext';
import AuthContext from '../contexts/AuthContext';
import axios from 'axios';

export default function AddNote() {
  const { state, dispatch } = useContext(NotesContext);
  const { state: authState } = useContext(AuthContext);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const token = authState.token;
  const isValid = title.trim() !== '' && content.trim() !== '';

  if (!token) return null;

  const saveNewNote = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const newNote = await axios.post(
        '/notes',
        {
          title,
          content,
          author: {
            name: authState.user?.name || '',
            email: authState.user?.email || '',
          },
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // **תיקון: להשתמש ב-res.data.notes אחרי הוספה**
      const currentNotes = state.cache[state.currentPage] || [];
      const updatedNotes = [newNote.data, ...currentNotes];

      dispatch({
        type: 'ADD_NOTE',
        payload: {
          notes: updatedNotes,
          total: state.total + 1,
        },
      });

      setTitle('');
      setContent('');
      setCreating(false);
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Added a new note' });
    } catch (err) {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to add note' });
    }
  };

  const cancelCreation = () => {
    setCreating(false);
    setTitle('');
    setContent('');
  };

  return creating ? (
    <form onSubmit={saveNewNote}>
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        name="text_input_new_note_title"
      />
      <textarea
        placeholder="Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        name="text_input_new_note_content"
      />
      <button type="submit" disabled={!isValid} name="text_input_save_new_note">
        Save
      </button>
      <button type="button" onClick={cancelCreation} name="text_input_cancel_new_note">
        Cancel
      </button>
    </form>
  ) : (
    <button onClick={() => setCreating(true)} name="add_new_note">
      Add New Note
    </button>
  );
}
