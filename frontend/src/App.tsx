import AddNote from './components/AddNote';
import NoteList from './components/NoteList';
import Pagination from './components/Pagination';
import Notification from './components/Notification';
import './App.css';

function App() {
  return (
    <>
      <Notification />
      <AddNote />
      <NoteList />
      <Pagination />
    </>
  );
}

export default App;
