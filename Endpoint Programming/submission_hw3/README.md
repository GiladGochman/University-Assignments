# HW3 Notes App

---

## Project Structure

```
SUBMISSION_HW1/
├── backend/            # Express API (TypeScript)
│   ├── config/         # Environment & DB setup
│   ├── controllers/    # Request handlers
│   ├── middlewares/    # auth and error handlers
│   ├── models/         # Mongoose schemas
│   ├── routes/         # Route definitions
│   ├── services/       # External service logic (if any)
│   ├── tests/          # Jest + Supertest tests
│   ├── expressApp.ts   # Express app definition
│   ├── server.ts       # Connect DB & start server
│   ├── tsconfig.json
│   ├── package.json
│   ├── jest.config.js
│   ├── .env            # (Not committed; listed in .gitignore)
│   └── .gitignore
│
├── frontend/           # React + TypeScript + Playwright tests
│   ├── src/            # Application source code
│   ├── tests/          # Playwright E2E tests
│   ├── tsconfig.json
│   ├── package.json
│   └── .gitignore
│
├── presubmission_tests/
├── presubmission.sh
└── README.md           # This file 
```

---

## Environment Setup

### Backend (`backend/.env`)

```dotenv
MONGODB_CONNECTION_URL=<your MongoDB connection string>
JWT_SECRET=<a long random secret>
PORT=3001
```

> **Security:** Do not commit `.env` to version control. Add it to `.gitignore`.

---

## Scripts & Commands

### Backend

```bash
cd backend
npm install

# Run in development mode (nodemon + ts-node)
npm run dev

# Compile TypeScript → dist/
npm run build

# Start production server from compiled code
npm run start

# Run Jest tests
npm test
```

### Frontend

```bash
cd frontend
npm install

# Run dev server\ npm run dev

# Build for production
npm run build

# Run Playwright tests
npx playwright test
```

---

## API Documentation

All endpoints are at `http://localhost:<PORT>` (default `3001`).

### Users

* **POST /users**

  * **Body**: `{ name, email, username, password }`
  * **Response**: `{ id, name, email, username }`
  * **Errors**:

    * `400 Bad Request` if missing fields

### Authentication (JWT)

* **POST /login**

  * **Body**: `{ username, password }`
  * **Response**: `{ token, username, name }`
  * **Errors**:

    * `401 Unauthorized` for invalid credentials

### Notes

* **GET /notes?page=<num>**

  * **Public**: no token required
  * **Response**: `{ notes: Note[], total, page, pages }`

* **POST /notes**

  * **Header**: `Authorization: Bearer <token>`
  * **Body**: `{ title, content }`
  * **Response**: created `Note` object (`201 Created`)
  * **Errors**:

    * `401 Unauthorized` if token is missing or invalid
    * `403 Forbidden` if user is not the owner

* **PUT /notes/\:id**

* **DELETE /notes/\:id**

  * **Header**: `Authorization: Bearer <token>`
  * **Response**: updated `Note` or `204 No Content`
  * **Errors**:

    * `401 Unauthorized` or `403 Forbidden` as above

#### Note Object Structure

```ts
interface Note {
  _id: string;
  title: string;
  content: string;
  author: { name: string; email: string };
  user: string;       // user ID of the creator
  createdAt: string;
  updatedAt: string;
}
```

---

## Automated Tests

### Backend Tests (Jest + Supertest)

* Location: `backend/tests/`
* Files: `users.test.ts`, `login.test.ts`, `notes.test.ts`
* Run with:

  ```bash
  cd backend
  npm test
  ```
* Tests will **not** delete existing users or notes. They only operate on test-specific data and validate CRUD behavior.

### Frontend Tests (Playwright)

* Location: `frontend/tests/`
* Run with:

  ```bash
  cd frontend
  npx playwright test
  ```

---

## Tips & Notes

* Keep your `JWT_SECRET` long and random, and never commit it to source control.
* Ensure Axios `baseURL` in frontend matches your chosen endpoint paths.

---

**Good luck!** 