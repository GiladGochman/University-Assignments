import React, {
  createContext,
  useReducer,
  useEffect,
  ReactNode,
  useContext,
} from 'react';
import axios from 'axios';
import { getPageNumbers } from '../components/getPageNumbers';
import AuthContext from './AuthContext';

export interface Note {
  id: string;
  title: string;
  author: { name: string; email: string } | null;
  content: string;
}

interface NotesState {
  cache: { [page: number]: Note[] };
  currentPage: number;
  total: number;
  notification: string;
}

type Action =
  | { type: 'SET_PAGE'; payload: number }
  | { type: 'SET_NOTES_FOR_PAGE'; page: number; notes: Note[] }
  | { type: 'SET_NOTIFICATION'; payload: string }
  | { type: 'UPDATE_NOTE'; payload: Note }
  | { type: 'DELETE_NOTE'; payload: { notes: Note[]; total: number } }
  | { type: 'ADD_NOTE'; payload: { notes: Note[]; total: number } }
  | { type: 'TRIM_CACHE'; allowedPages: number[] }
  | { type: 'SET_TOTAL'; total: number };

const initialState: NotesState = {
  cache: {},
  currentPage: 1,
  total: 0,
  notification: 'Notification area',
};

const NotesContext = createContext<{
  state: NotesState;
  dispatch: React.Dispatch<Action>;
}>({
  state: initialState,
  dispatch: () => {},
});

const notesReducer = (state: NotesState, action: Action): NotesState => {
  switch (action.type) {
    case 'SET_PAGE':
      return { ...state, currentPage: action.payload };
    case 'SET_NOTES_FOR_PAGE':
      return {
        ...state,
        cache: { ...state.cache, [action.page]: action.notes },
      };
    case 'SET_NOTIFICATION':
      return { ...state, notification: action.payload };
    case 'UPDATE_NOTE': {
      const updated = state.cache[state.currentPage]?.map((n) =>
        n.id === action.payload.id ? action.payload : n
      );
      return {
        ...state,
        cache: { ...state.cache, [state.currentPage]: updated },
        notification: 'Note updated',
      };
    }
    case 'DELETE_NOTE':
      return {
        ...state,
        cache: { ...state.cache, [state.currentPage]: action.payload.notes },
        total: action.payload.total,
        notification: 'Note deleted',
      };
    case 'ADD_NOTE':
      return {
        ...state,
        cache: { ...state.cache, [state.currentPage]: action.payload.notes },
        total: action.payload.total,
        notification: 'Added a new note',
      };
    case 'TRIM_CACHE': {
      const newCache: typeof state.cache = {};
      for (const page of action.allowedPages) {
        if (state.cache[page]) {
          newCache[page] = state.cache[page];
        }
      }
      return { ...state, cache: newCache };
    }
    case 'SET_TOTAL':
      return { ...state, total: action.total };
    default:
      return state;
  }
};

export const NotesProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(notesReducer, initialState);
  const { state: authState } = useContext(AuthContext);

  useEffect(() => {
    const updateCache = async () => {
      const totalPages = Math.ceil(state.total / 10);
      const pagesToFetch = getPageNumbers(state.currentPage, totalPages);

      const fetchedPages = await Promise.all(
        pagesToFetch.map(async (p) => {
          if (!state.cache[p]) {
            const res = await axios.get(`/notes?_page=${p}&_limit=10`);
            return { page: p, notes: res.data.notes };
          }
          return null;
        })
      );

      fetchedPages.forEach((entry) => {
        if (entry) {
          dispatch({ type: 'SET_NOTES_FOR_PAGE', page: entry.page, notes: entry.notes });
        }
      });

      dispatch({ type: 'TRIM_CACHE', allowedPages: pagesToFetch });
    };

    updateCache();
  }, [state.currentPage, authState.token, state.total]);

  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const res = await axios.get(`/notes?_page=1&_limit=10`);
        const totalCount = res.data.total;  
        dispatch({ type: 'SET_TOTAL', total: totalCount });
        dispatch({ type: 'SET_NOTES_FOR_PAGE', page: 1, notes: res.data.notes });
      } catch (err) {
        console.error('Error fetching notes:', err);
      }
    };

    if (state.total === 0) {
      fetchInitial();
    }
  }, []);

  return (
    <NotesContext.Provider value={{ state, dispatch }}>
      {children}
    </NotesContext.Provider>
  );
};

export const useNotes = () => useContext(NotesContext);

export default NotesContext;
