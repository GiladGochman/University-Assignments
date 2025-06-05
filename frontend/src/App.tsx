import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
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

  const [activePage, setActivePage] = useState(1); // Track active page with useState
  const [notes, setNotes] = useState<Note[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const NOTES_URL = "http://localhost:3001/notes";
  const POSTS_PER_PAGE = 10;

  // Fetch the notes when activePage changes
  useEffect(() => {
    axios
      .get(NOTES_URL, {
        params: {
          _page: activePage,
          _limit: POSTS_PER_PAGE,
        },
      })
      .then((response) => {
        setNotes(response.data);
        const total = response.headers["x-total-count"];
        console.log("Total pages calculated:", total);
        setTotalPages(() => Math.ceil(Number(total) / POSTS_PER_PAGE));
      })
      .then()
      .catch((error) => {
        console.log("Encountered an error:", error);
      });
  }, [activePage]);

  function getPageRange(activePage: number, totalPages: number): number[] {
    if (totalPages <= 5) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    if (activePage <= 3) {
      return [1, 2, 3, 4, 5];
    }

    if (activePage >= totalPages - 2) {
      return Array.from({ length: 5 }, (_, i) => totalPages - 4 + i); //i starts at 0 and grows up to 4
    }

    return [
      activePage - 2,
      activePage - 1,
      activePage,
      activePage + 1,
      activePage + 2,
    ];
  }

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

      {}
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

      {}
      <span>
        page: {activePage} / {totalPages}
      </span>

      <div>
        <button
          name="first"
          disabled={activePage === 1}
          onClick={() => setActivePage(() => 1)}
        >
          first
        </button>
        <button
          name="previous"
          disabled={activePage === 1}
          onClick={() => setActivePage((prevPage) => Math.max(prevPage - 1, 1))}
        >
          previous
        </button>
        {getPageRange(activePage, totalPages).map((page) => (
          <button
            key={page}
            name={`page-${page}`}
            disabled={activePage === page}
            className={`${page === activePage ? "active" : "not-active"}`}
            onClick={() => setActivePage(page)}
          >
            {page}
          </button>
        ))}
        <button
          name="next"
          disabled={activePage === totalPages}
          onClick={() =>
            activePage < totalPages
              ? setActivePage((prevPage) => prevPage + 1)
              : {}
          }
        >
          Next
        </button>
        <button
          name="last"
          disabled={activePage === totalPages}
          onClick={() => setActivePage(() => totalPages)}
        >
          last
        </button>
      </div>
    </>
  );
}

export default App;
