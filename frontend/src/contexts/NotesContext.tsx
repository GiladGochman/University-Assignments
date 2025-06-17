import React, {
  createContext,
  useReducer,
  useContext,
  useEffect,
  ReactNode,
} from 'react';
import axios from 'axios';
import { fetchNotesWithCache } from '../services/notesLoader';


export interface Note {
  _id: string;
  title: string;
  content: string;
  author: {
    name: string;
    email: string;
  };
}

interface State {
  notes: Note[];
  totalPages: number;
  currentPage: number;
  notification: string;
  cache: Record<number, Note[]>;
}

type Action =
  | { type: 'SET_NOTES'; payload: { notes: Note[]; totalPages: number } }
  | { type: 'ADD_NOTE'; payload: Note }
  | { type: 'UPDATE_NOTE'; payload: Note }
  | { type: 'DELETE_NOTE'; payload: string }
  | { type: 'SET_PAGE'; payload: number }
  | { type: 'SET_NOTIFICATION'; payload: string }
  | { type: 'SET_CACHE_PAGE'; payload: { page: number; notes: Note[] } };

const initialState: State = {
  notes: [],
  totalPages: 1,
  currentPage: 1,
  notification: '',
  cache: {},
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_NOTES':
      return { ...state, notes: action.payload.notes, totalPages: action.payload.totalPages };
    case 'ADD_NOTE':
      return {
        ...state,
        notes: [action.payload, ...state.notes],
        notification: 'Added a new note',
        cache: {}, // invalidate cache
      };
    case 'UPDATE_NOTE':
      return {
        ...state,
        notes: state.notes.map((n) =>
          n._id === action.payload._id ? action.payload : n
        ),
        notification: 'Note updated',
        cache: {},
      };
    case 'DELETE_NOTE':
      return {
        ...state,
        notes: state.notes.filter((n) => n._id !== action.payload),
        notification: 'Note deleted',
        cache: {},
      };
    case 'SET_PAGE':
      return { ...state, currentPage: action.payload };
    case 'SET_NOTIFICATION':
      return { ...state, notification: action.payload };
    case 'SET_CACHE_PAGE':
      return {
        ...state,
        cache: { ...state.cache, [action.payload.page]: action.payload.notes },
      };
    default:
      return state;
  }
}

const NotesContext = createContext<
  | {
      state: State;
      dispatch: React.Dispatch<Action>;
    }
  | undefined
>(undefined);

export const NotesProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    fetchNotesWithCache(
      state.currentPage,
      state.cache,
      dispatch,
      state.totalPages,
      import.meta.env.VITE_BACKEND_URL
    );
  }, [state.currentPage]);

  return (
    <NotesContext.Provider value={{ state, dispatch }}>
      {children}
    </NotesContext.Provider>
  );
};

export const useNotes = () => {
  const ctx = useContext(NotesContext);
  if (!ctx) throw new Error('useNotes must be used within NotesProvider');
  return ctx;
};
