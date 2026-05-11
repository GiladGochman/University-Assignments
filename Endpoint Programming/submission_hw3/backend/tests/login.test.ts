import request from 'supertest';
import mongoose from 'mongoose';
import app from '../expressApp'; 
import { User } from '../models/User';

beforeAll(async () => {
  // Connect to the test database
  await mongoose.connect(process.env.MONGODB_CONNECTION_URL!);
  
  const existing = await User.findOne({ username: 'testuser' });
  if (!existing) {
    await request(app)
      .post('/users')           
      .send({
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        password: 's3cret'
      })
      .expect(201);
  }
});

afterAll(async () => {
  // Clean up the test user
  await User.deleteOne({ username: 'testuser' });
  // Disconnect from the database
  await mongoose.disconnect();
});

describe('POST /login', () => {
  it('returns 200 and a token for valid credentials', async () => {
    const res = await request(app)
      .post('/login')
      .send({ username: 'testuser', password: 's3cret' })
      .expect(200)
      .expect('Content-Type', /application\/json/);

    expect(res.body).toHaveProperty('token');
    expect(res.body).toMatchObject({
      username: 'testuser',
      name: 'Test User'
    });
  });

  it('returns 401 for wrong password', async () => {
    await request(app)
      .post('/login')
      .send({ username: 'testuser', password: 'wrongpass' })
      .expect(401)
      .expect(res => {
        expect(res.body.error).toBe('invalid credentials');
      });
  });

  it('returns 401 for non‐existent user', async () => {
    await request(app)
      .post('/login')
      .send({ username: 'nouser', password: 'whatever' })
      .expect(401)
      .expect(res => {
        expect(res.body.error).toBe('invalid credentials');
      });
  });
});