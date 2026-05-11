// src/contexts/NotesContext.tsx
import React, {
  createContext,
  useReducer,
  useContext,
  ReactNode,
  useState,
} from "react";
import { Note } from "../types/Note";

// --- Action types ---
type NotesAction =
  | { type: "SET_NOTES"; payload: Note[] }
  | { type: "ADD_NOTE"; payload: Note }
  | { type: "UPDATE_NOTE"; payload: Note }
  | { type: "DELETE_NOTE"; payload: string };

// --- State type ---
interface NotesState {
  notes: Note[];
}

// --- Context interface ---
interface NotesContextProps {
  state: NotesState;
  dispatch: React.Dispatch<NotesAction>;
  notification: string;
  setNotification: React.Dispatch<React.SetStateAction<string>>;
}

// --- Initial state ---
const initialState: NotesState = {
  notes: [],
};

// --- Reducer ---
function notesReducer(state: NotesState, action: NotesAction): NotesState {
  switch (action.type) {
    case "SET_NOTES":
      return { ...state, notes: action.payload };
    case "ADD_NOTE":
      return { ...state, notes: [action.payload, ...state.notes] };
    case "UPDATE_NOTE":
      return {
        ...state,
        notes: state.notes.map((note) =>
          note._id === action.payload._id ? action.payload : note
        ),
      };
    case "DELETE_NOTE":
      return {
        ...state,
        notes: state.notes.filter((note) => note._id !== action.payload),
      };
    default:
      return state;
  }
}

// --- Create context ---
export const NotesContext = createContext<NotesContextProps | undefined>(
  undefined
);

// --- Provider ---
export const NotesProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(notesReducer, initialState);
  const [notification, setNotification] = useState("");

  return (
    <NotesContext.Provider
      value={{ state, dispatch, notification, setNotification }}
    >
      {children}
    </NotesContext.Provider>
  );
};

export const useNotesContext = () => {
  const context = useContext(NotesContext);
  if (!context) {
    throw new Error("useNotesContext must be used within a NotesProvider");
  }
  return context;
};
