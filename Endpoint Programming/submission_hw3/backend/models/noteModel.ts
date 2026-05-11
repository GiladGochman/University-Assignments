import { Schema, model, Document, Types } from 'mongoose';

export interface INote extends Document {
  title: string;
  content: string;
  author: { name: string; email: string };
  user: Types.ObjectId;
}

const noteSchema = new Schema<INote>({
  title: { type: String, required: true },
  content: { type: String, required: true },
  author: {
    name: String,
    email: String
  },
  user: { type: Schema.Types.ObjectId, ref: 'User', required: true }
}, { timestamps: true });

export const Note = model<INote>('Note', noteSchema);