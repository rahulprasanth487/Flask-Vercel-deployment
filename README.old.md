# React + FastAPI + Mongo demo (for Vercel)

This repository contains a minimal example of a React frontend and a FastAPI backend that uses MongoDB (Motor). It's configured so you can deploy to Vercel: the React `build` is served as static files and the FastAPI app is deployed as a Python serverless function.

Local run (development)

- Start MongoDB (local or use a hosted Mongo URI)
- Start the FastAPI app (we use a root-path so the frontend can call `/api/todos`):

```powershell
cd api
# create venv, activate and install requirements
python -m venv venv; venv\Scripts\Activate;
pip install -r requirements.txt

# Run uvicorn with the root path so the endpoint is available at /api/todos
uvicorn api.todos:app --reload --port 5000 --root-path /api/todos
```

- Start the React dev server (from project root or another terminal):

```powershell
cd frontend
npm install
npm start
```

The CRA dev server is configured with a proxy (`http://localhost:5000`) so requests to `/api/todos` will be proxied to the FastAPI server.

Deploy to Vercel

1. Ensure you have a Vercel account and the `vercel` CLI installed (optional).
2. Set the environment variable `MONGODB_URI` in Vercel dashboard (or use a hosted Mongo Atlas URI).
3. From the project root run:

```powershell
vercel deploy --prod
```

Notes
- The Python serverless file is `api/todos.py`. Vercel will map `/api/todos` to that function.
- Keep your `MONGODB_URI` secret and set it in Vercel's Environment Variables.
