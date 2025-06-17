import { useNavigate } from "react-router-dom";
import { useNotes } from "../contexts/NotesContext";
import { useAuth } from "../contexts/AuthContext";
import AddNote from "../components/AddNote";
import NoteList from "../components/NoteList";
import Pagination from "../components/Pagination";

export default function Home() {
  const { dispatch } = useNotes();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    dispatch({ type: "SET_NOTIFICATION", payload: "Logged out" });
  };

  return (
    <div>
      <h1>Notes</h1>

      {user ? (
        <>
          <button data-testid="logout" onClick={handleLogout}>
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
