import { useState, useEffect } from "react";
import { getNotesPage } from "../services/notes"; 

type Note = {
  _id: string;
  title: string;
  content: string;
  author: {
    name: string;
    email: string;
  };
};

type Cache = Record<number, Note[]>;

export function useNoteCache(currentPage: number): Note[] {
  const [cache, setCache] = useState<Cache>({});

  useEffect(() => {
    const pagesToCache = [currentPage - 2, currentPage - 1, currentPage, currentPage + 1, currentPage + 2]
      .filter((p) => p > 0);

    const fetchMissingPages = async () => {
      const newCache = { ...cache };

      for (const page of pagesToCache) {
        if (!newCache[page]) {
          try {
            const notes = await getNotesPage(page); // מביא מהשרת לפי עמוד
            newCache[page] = notes;
          } catch (err) {
            console.error("Error fetching page", page, err);
          }
        }
      }

      setCache(newCache);
    };

    fetchMissingPages();
  }, [currentPage]);

  return cache[currentPage] || [];
}
