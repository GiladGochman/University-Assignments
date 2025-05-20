import  Note from '../models/noteModel';

export const getAllNotes = async (page = 1, perPage = 10) => {
  const skip = (page - 1) * perPage;
  const notes = await Note.find().sort({ _id: -1 }).skip(skip).limit(perPage);
  const count = await Note.countDocuments();
  return { notes, count };
};

export const getNoteById = async (id: string) => {
  return await Note.findById(id);
};

export const createNote = async (data: any) => {
  return await Note.create(data);
};

export const updateNoteById = async (id: string, data: any) => {
  return await Note.findByIdAndUpdate(id, data, { new: true });
};

export const deleteNoteById = async (id: string) => {
  return await Note.findByIdAndDelete(id);
};

export const getNoteByIndex = async (index: number) => {
  const notes = await Note.find().sort({ _id: -1 }).skip(index).limit(1);
  return notes[0] || null;
};

export const updateNoteByIndex = async (index: number, data: any) => {
  const note = await getNoteByIndex(index);
  if (!note) return null;
  return await Note.findByIdAndUpdate(note._id, data, { new: true });
};

export const deleteNoteByIndex = async (index: number) => {
  const note = await getNoteByIndex(index);
  if (!note) return null;
  return await Note.findByIdAndDelete(note._id);
};