import axios from "axios";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:3001";

export async function getNotesPage(page: number, perPage: number = 10) {
  const response = await axios.get(`${BASE_URL}/notes?page=${page}&perPage=${perPage}`);
  return response.data.notes;
}

export async function addNote(
  note: { title: string; content: string },
  token: string
) {
  const response = await axios.post(`${BASE_URL}/notes`, note, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

export async function updateNote(
  id: string,
  data: { title: string; content: string },
  token: string
) {
  const response = await axios.put(`${BASE_URL}/notes/${id}`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

export async function deleteNote(id: string, token: string) {
  const response = await axios.delete(`${BASE_URL}/notes/${id}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}
