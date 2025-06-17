// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { NotesProvider } from "./contexts/NotesContext";
import { AuthProvider } from "./contexts/AuthContext"; // 👈 ייבוא חדש

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider> 
      <NotesProvider>
        <App />
      </NotesProvider>
    </AuthProvider>
  </React.StrictMode>
);
