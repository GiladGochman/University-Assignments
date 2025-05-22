import { useState } from 'react';
import { useNotes } from '../contexts/NotesContext';

export default function AddNote() {
  const { dispatch } = useNotes();
  const [adding, setAdding] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [newTitle, setNewTitle] = useState('');

  const handleAddNote = async () => {
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: newTitle || 'Untitled',
        content: newContent,
        author: { name: 'Rotem', email: 'rotem@example.com' }
      }),
    });

    const created = await res.json();
    dispatch({ type: 'ADD_NOTE', payload: created });
    dispatch({ type: "SET_NOTIFICATION" , payload: 'Added a new note' });
    setNewTitle('');
    setNewContent('');
    setAdding(false);
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
      <button name="text_input_save_new_note" onClick={handleAddNote}>Save</button>
      <button name="text_input_cancel_new_note" onClick={() => setAdding(false)}>Cancel</button>
    </div>
  ) : (
    <button name="add_new_note" onClick={() => setAdding(true)}>Add New Note</button>
  );
}
