import { useNotes } from '../contexts/NotesContext';

export default function Notification() {
  const { state } = useNotes();
  const { notification } = state;

  return <div className="notification">{notification}</div>;
}
