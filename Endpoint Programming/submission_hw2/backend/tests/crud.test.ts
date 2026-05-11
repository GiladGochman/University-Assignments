import request from "supertest";
import mongoose from "mongoose";
import { MongoMemoryServer } from "mongodb-memory-server";
import app from "../expressApp";
import { Note } from "../models/note";

let mongoServer: MongoMemoryServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const uri = mongoServer.getUri();
  await mongoose.connect(uri);
});

afterAll(async () => {
  await mongoose.connection.close();
  await mongoServer.stop();
});

afterEach(async () => {
  await Note.deleteMany({});
});

describe("CRUD tests for /notes", () => {
  test("POST /notes - creates a note", async () => {
    const newNote = {
      title: "Test Note",
      author: { name: "Alice", email: "alice@example.com" },
      content: "This is a test",
    };

    const res = await request(app).post("/notes").send(newNote);

    expect(res.status).toBe(201);
    expect(res.body.title).toBe(newNote.title);
    expect(res.body.author.name).toBe("Alice");
  });

  test("GET /notes/:id - retrieves a note", async () => {
    const note = await Note.create({
      title: "Another Note",
      author: { name: "Bob", email: "bob@example.com" },
      content: "Sample content",
    });

    const res = await request(app).get(`/notes/${note._id}`);
    expect(res.status).toBe(200);
    expect(res.body.title).toBe("Another Note");
  });

  test("PUT /notes/:id - updates a note", async () => {
    const note = await Note.create({
      title: "Old Title",
      author: null,
      content: "Old content",
    });

    const res = await request(app)
      .put(`/notes/${note._id}`)
      .send({ title: "Updated Title", content: "Updated content" });

    expect(res.status).toBe(200);
    expect(res.body.title).toBe("Updated Title");
  });

  test("DELETE /notes/:id - deletes a note", async () => {
    const note = await Note.create({
      title: "To be deleted",
      author: null,
      content: "...",
    });

    const res = await request(app).delete(`/notes/${note._id}`);
    expect(res.status).toBe(204);

    const check = await Note.findById(note._id);
    expect(check).toBeNull();
  });
});
