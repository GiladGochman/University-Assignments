// src/services/notesLoader.ts
import axios from 'axios';
import { Note } from '../contexts/NotesContext';

export function getPaginationWindow(currentPage: number): number[] {
  const window: number[] = [];
  for (let i = currentPage - 2; i <= currentPage + 2; i++) {
    if (i >= 1) window.push(i);
  }
  return window;
}

export async function fetchNotesWithCache(
  currentPage: number,
  cache: Record<number, Note[]>,
  dispatch: any,
  totalPages: number,
  backendUrl: string
) {
  if (cache[currentPage]) {
    dispatch({
      type: 'SET_NOTES',
      payload: {
        notes: cache[currentPage],
        totalPages,
      },
    });
  } else {
    try {
      const res = await axios.get(`${backendUrl}/notes`, {
        params: { _page: currentPage, _per_page: 10 },
      });

      const total = parseInt(res.headers['x-total-count'], 10);
      dispatch({
        type: 'SET_NOTES',
        payload: {
          notes: res.data.notes,
          totalPages: res.data.pages, // או Math.ceil(res.data.total / 10)
        },
      });
      dispatch({
        type: 'SET_CACHE_PAGE',
        payload: {
          page: currentPage,
          notes: res.data.notes,
        },
      });
    } catch {
      dispatch({ type: 'SET_NOTIFICATION', payload: 'Failed to fetch notes' });
    }
  }

  // Prefetch nearby pages
  const pagesToPrefetch = getPaginationWindow(currentPage);
  for (const page of pagesToPrefetch) {
    if (page !== currentPage && !cache[page]) {
      try {
        const res = await axios.get(`${backendUrl}/notes`, {
          params: { _page: page, _per_page: 10 },
        });
        dispatch({
          type: 'SET_CACHE_PAGE',
          payload: { page, notes: res.data },
        });
      } catch (e) {
        console.error(`Prefetch for page ${page} failed`, e);
      }
    }
  }
}
