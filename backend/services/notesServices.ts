import { Note } from "../models/note";
import { Types } from "mongoose";

export const getAllNotes = async () => {
  return await Note.find().exec();
};

export const getNoteById = async (id: string) => {
  if (!Types.ObjectId.isValid(id)) return null;
  return await Note.findById(id).exec();
};

export const getNoteByIndex = async (index: number) => {
  const notes = await Note.find()
    .sort({ createdAt: 1 })
    .skip(index)
    .limit(1)
    .exec();
  return notes[0] || null;
};

export const createNote = async (data: {
  title: string;
  content: string;
  author: { name: string; email: string };
}) => {
  const note = new Note(data);
  return await note.save();
};

export const updateNote = async (
  id: string,
  data: { title?: string; content?: string }
) => {
  if (!Types.ObjectId.isValid(id)) return null;
  return await Note.findByIdAndUpdate(id, data, { new: true }).exec();
};

export const deleteNote = async (id: string) => {
  if (!Types.ObjectId.isValid(id)) return null;
  return await Note.findByIdAndDelete(id).exec();
};
