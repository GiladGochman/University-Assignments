## Optional: Run local server with an input JSON file:
```bash
 npx json-server --port 3001 --watch ./data/notes.json
```

(can be accessed with:  http://localhost:3001/notes?_page=1&_limit=10  for example) 


## 1.Run your code:

```bash
 cd <vite_project_path>
 npm run dev
```

## 2. Run api router to backend server:
```bash
 cd ./backend
 npx ts-node index.ts
```

(can be accessed with:  http://localhost:3001/api/notes/) 

 
