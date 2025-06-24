import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import AddNote from "./components/AddNote";
import NoteList from "./components/NoteList";
import Pagination from "./components/Pagination";
import Notification from "./components/Notification";
import Login from "./pages/Login";
import CreateUser from "./pages/CreateUser";
import Home from "./pages/Home";
import Me from "./pages/Me";
import { NotesProvider } from "./contexts/NotesContext";

function App() {
  return (
    <NotesProvider>
      <Router>
        <Notification />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-user" element={<CreateUser />} />
          <Route path="/me" element={<Me />} /> {/* הוסף את זה */}
        </Routes>
      </Router>
    </NotesProvider>
  );
}

export default App;
