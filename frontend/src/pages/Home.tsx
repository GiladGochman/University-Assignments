import { useNavigate } from "react-router-dom";
import { useNotes } from "../contexts/NotesContext";
import AddNote from "../components/AddNote";
import NoteList from "../components/NoteList";
import Pagination from "../components/Pagination";

export default function Home() {
  const { state, dispatch } = useNotes();
  const { user } = state;
  const navigate = useNavigate();

  return (
    <div>
      <h1>Notes</h1>

      {user ? (
        <>
          <button data-testid="logout" onClick={() => dispatch({ type: "LOGOUT" })}>
            Logout
          </button>
          <AddNote />
        </>
      ) : (
        <>
          <button data-testid="go_to_login_button" onClick={() => navigate("/login")}>
            Go to Login
          </button>
          <button data-testid="go_to_create_user_button" onClick={() => navigate("/create-user")}>
            Create New User
          </button>
        </>
      )}

      <NoteList />
      <Pagination />
    </div>
  );
}
