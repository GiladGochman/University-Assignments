import { useEffect, useState } from "react";
import axios from "axios";
import NoteList from "./components/noteList";
import Pagination from "./components/pagination";
import EditData from "./components/editData";

import { Note } from "./types/Note";
import "./App.css";
// import reactLogo from "./assets/react.svg";
// import viteLogo from "./assets/vite.svg";

function App() {
  const [activePage, setActivePage] = useState(1);
  const [notes, setNotes] = useState<Note[]>([]);
  const [totalPages, setTotalPages] = useState(1);

  const NOTES_URL = "http://localhost:3001/notes";
  const POSTS_PER_PAGE = 10;

  useEffect(() => {
    axios
      .get(`${NOTES_URL}/page/${activePage}`)
      .then((response) => {
        setNotes(response.data);
        // כאן תוכל לעדכן לפי כמות כוללת, אם תתמוך בזה בצד שרת
        // setTotalPages(...);
      })
      .catch((err) => console.error("Error fetching notes:", err));
  }, [activePage]);

  return (
    <>
      {/* <a href="https://vite.dev" target="_blank">
        <img src={viteLogo} className="logo" alt="Vite logo" />
      </a> */}
      <EditData />
      <NoteList notes={notes} />
      <Pagination
        activePage={activePage}
        totalPages={totalPages}
        setActivePage={setActivePage}
      />
    </>
  );
}

export default App;
