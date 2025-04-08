import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import axios from "axios";

function App() {
  interface Note {
    id: number;
    title: string;
    author: string;
    content: string;
  }

  const [count, setCount] = useState(0);

  const NOTES_URL = "http://localhost:3001/notes";
  const POSTS_PER_PAGE = 10;
  let activePage = 0;

  const NotesList: React.FC = () => {
    const [notes, setNotes] = useState<Note[]>([]);

    useEffect(() => {
      const promise = axios.get(NOTES_URL, {
        params: {
          _page: activePage,
          _per_page: POSTS_PER_PAGE,
        },
      });
      promise
        .then((response) => {
          // fill
          setNotes(response.data);
        })
        .catch((error) => {
          console.log("Encountered an error:" + error);
        });
    }, []);

    return (
      <div>
        {notes.map((note) => (
          <div key={note.id} className="note" id={note.id.toString()}>
            <h2>{note.title}</h2>
            <small>By {note.author}</small>
            <br />
            {note.content}
          </div>
        ))}
      </div>
    );
  };

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
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
