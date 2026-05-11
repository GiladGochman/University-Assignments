import { useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../contexts/AuthContext';
import LogoutButton from '../components/Logout';
import NoteList from '../components/NoteList';
import AddNote from '../components/AddNote';  // תוקן כאן: הוסר הרווח בין 'compon' ל'ents'
import Pagination from '../components/Pagination';

const Home = () => {
  const { state } = useContext(AuthContext);
  const user = state.user;

  return (
    <div>
      <h1>Homepage</h1>

      {!user ? (
        <>
          <Link to="/login">
            <button data-testid="go_to_login_button">Go to Login</button>
          </Link>
          <Link to="/create-user">
            <button data-testid="go_to_create_user_button">Create New User</button>
          </Link>
        </>
      ) : (
        <>
          <LogoutButton />
          <AddNote />
        </>
      )}

      <NoteList />
      <Pagination />
    </div>
  );
};

export default Home;
