## 1. Run backend server locally:

```bash
 cd <vite_project_path>/backend
 npm run dev
```

(can be accessed with: http://localhost:3000)

## 2. Run frontend locally:

```bash
 cd <vite_project_path>/frontend
 npm run dev
```

(can be accessed with: http://localhost:3001/notes/ for all notes)
( http://localhost:3001/notes/page/1 for first page)

## Optional: Run local server with an input JSON file:

```bash
 npx json-server --port 3001 --watch ./data/notes.json
```

(can be accessed with: http://localhost:3001/notes?\_page=1&\_limit=10 for example)
