// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { NotesProvider } from "./contexts/NotesContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <NotesProvider>
      <App />
    </NotesProvider>
  </React.StrictMode>
);
