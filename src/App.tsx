import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import axios from "axios";

function App() {
  interface Note {
    id: number;
    title: string;
    author: {
      name: string;
      email: string;
    };
    content: string;
  }

  const [count, setCount] = useState(0);
  const [activePage, setActivePage] = useState(1); // Track active page with useState
  const [notes, setNotes] = useState<Note[]>([]);

  const NOTES_URL = "http://localhost:3001/notes";
  const POSTS_PER_PAGE = 10;

  // Fetch the notes when activePage changes
  useEffect(() => {
    axios
      .get(NOTES_URL, {
        params: {
          _page: activePage,
          _limit: POSTS_PER_PAGE, // Update _per_page to _limit as per json-server
        },
      })
      .then((response) => {
        setNotes(response.data); // Fill the notes
      })
      .catch((error) => {
        console.log("Encountered an error:", error);
      });
  }, [activePage]); // Dependency on activePage so it re-runs when page changes

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>

      {/* Render the notes */}
      <div>
        {notes.map((note) => (
          <div key={note.id} className="note" id={note.id.toString()}>
            <h2>{note.title}</h2>
            <small>By {note.author.name}</small>
            <br />
            {note.content}
          </div>
        ))}
      </div>

      {/* Add Pagination Controls */}
      <div>
        <button
          onClick={() => setActivePage((prevPage) => Math.max(prevPage - 1, 1))}
        >
          Prev
        </button>
        <button onClick={() => setActivePage((prevPage) => prevPage + 1)}>
          Next
        </button>
      </div>
    </>
  );
}

export default App;
