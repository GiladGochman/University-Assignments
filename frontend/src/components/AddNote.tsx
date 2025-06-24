import { useState } from 'react';
import { useNotes } from '../contexts/NotesContext';
import { addNote } from '../services/notes';

export default function AddNote() {
  const { dispatch } = useNotes();
  const [adding, setAdding] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [newTitle, setNewTitle] = useState('');

  const token = localStorage.getItem('user-token');

  const handleAddNote = async () => {
    if (!token) {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'You must be logged in' });
      return;
    }

    try {
      const created = await addNote(
        { title: newTitle || 'Untitled', content: newContent },
        token
      );
      dispatch({ type: 'ADD_NOTE', payload: created });
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Added a new note' });
      setNewTitle('');
      setNewContent('');
      setAdding(false);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to add note' });
    }
  };

  return adding ? (
    <div>
      <input
        type="text"
        placeholder="Title"
        value={newTitle}
        onChange={(e) => setNewTitle(e.target.value)}
        name="text_input_title_new_note"
      />
      <input
        type="text"
        value={newContent}
        name="text_input_new_note"
        onChange={(e) => setNewContent(e.target.value)}
      />
      <button name="text_input_save_new_note" onClick={handleAddNote}>
        Save
      </button>
      <button name="text_input_cancel_new_note" onClick={() => setAdding(false)}>
        Cancel
      </button>
    </div>
  ) : (
    <button name="add_new_note" onClick={() => setAdding(true)}>
      Add New Note
    </button>
  );
}
