import request from 'supertest';
import mongoose from 'mongoose';
import app from '../expressApp'; 
import { Note } from '../models/noteModel';
import { User } from '../models/User';

let token: string;
let createdNoteId: string;

beforeAll(async () => {
  await mongoose.connect(process.env.MONGODB_CONNECTION_URL!);

  const existing = await User.findOne({ username: 'noteuser' });
  if (!existing) {
    await request(app)
      .post('/users')
      .send({
        name: 'Note User',
        email: 'note@x.com',
        username: 'noteuser',
        password: 'pass123'
      })
      .expect(201);
  }

  const res = await request(app)
    .post('/login')
    .send({ username: 'noteuser', password: 'pass123' })
    .expect(200);
  token = res.body.token;
});

afterAll(async () => {
  // Clean up the test user and notes
  await User.deleteOne({ username: 'noteuser' });
  await Note.deleteMany({ user: (await User.findOne({ username: 'noteuser' }))?._id });
  // Disconnect from the database
  await mongoose.disconnect();
});

describe('Notes', () => {
  it('GET /notes?page=1 should return an object', async () => {
    const res = await request(app)
      .get('/notes?page=1')
      .expect(200);
    expect(res.body).toHaveProperty('notes');
  });

  it('POST /notes should create a note when authenticated', async () => {
    const res = await request(app)
      .post('/notes')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'First Note', content: 'Hello World' })
      .expect(201);

    expect(res.body).toMatchObject({
      title: 'First Note',
      content: 'Hello World',
      author: { name: 'Note User', email: 'note@x.com' }
    });
    createdNoteId = res.body._id;
  });

  it('PUT /notes/:id should update note when owner', async () => {
    const updated = await request(app)
      .put(`/notes/${createdNoteId}`)
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'Updated', content: 'Content' })
      .expect(200);

    expect(updated.body.title).toBe('Updated');
  });

  it('DELETE /notes/:id should remove note when owner', async () => {
    await request(app)
      .delete(`/notes/${createdNoteId}`)
      .set('Authorization', `Bearer ${token}`)
      .expect(204);

    const all = await request(app)
      .get('/notes?page=1')
      .expect(200);
    expect(all.body.notes.some((n: any) => n._id === createdNoteId)).toBe(false);
  });

  it('POST /notes without token returns 401', async () => {
    await request(app)
      .post('/notes')
      .send({ title: 'No Auth', content: 'fail' })
      .expect(401);
  });
});
