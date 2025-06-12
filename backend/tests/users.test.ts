import request from 'supertest';
import mongoose from 'mongoose';
import app from '../expressApp';
import { User } from '../models/User';

beforeAll(async () => {
  await mongoose.connect(process.env.MONGODB_CONNECTION_URL!);

  // remove any leftover test user "b"
  await User.deleteOne({ username: 'b' });
});

afterAll(async () => {
  // clean up the user we created
  await User.deleteOne({ username: 'b' });
  await mongoose.disconnect();
});

describe('Users API', () => {
  it('creates user when missing', async () => {
    const res = await request(app)
      .post('/users')
      .send({
        name:     'B',
        email:    'b@x.com',
        username: 'b',
        password: 'pass2'
      })
      .expect(201);
    expect(res.body).toMatchObject({ name: 'B', username: 'b' });
  });

  it('fails on missing password', async () => {
    await request(app)
      .post('/users')
      .send({ username: 'c' })
      .expect(400);
  });
});