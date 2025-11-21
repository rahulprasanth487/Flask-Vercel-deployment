import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  // Detect environment: if deployed, use /api/todos
  const API_BASE =
    window.location.hostname === 'localhost'
      ? 'http://127.0.0.1:5000/api/todos'
      : '/api/todos';

  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Do not auto-fetch todos on page load. Waiting for user action.
  }, []);

  async function fetchTodos() {
    setLoading(true);
    try {
      const res = await fetch(API_BASE);
      if (!res.ok) {
        console.error('fetchTodos failed', res.status);
        return;
      }
      const data = await res.json();
      setTodos(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('fetchTodos error', err);
    } finally {
      setLoading(false);
    }
  }

  // Fetch sample todos from the health endpoint (no MongoDB touch)
  async function fetchSampleTodos() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) {
        console.error('fetchSampleTodos failed', res.status);
        return;
      }
      const data = await res.json();
      // Health endpoint returns { status, todos }
      if (data && Array.isArray(data.todos)) setTodos(data.todos);
    } catch (err) {
      console.error('fetchSampleTodos error', err);
    } finally {
      setLoading(false);
    }
  }

  async function addTodo(e) {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      const res = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim() }),
      });

      if (!res.ok) {
        console.error('addTodo failed', res.status);
        return;
      }

      const newTodo = await res.json();
      setTodos((prev) => [newTodo, ...prev]);
      setTitle('');
    } catch (err) {
      console.error('addTodo error', err);
    }
  }

  async function toggleDone(todo) {
    try {
      const res = await fetch(`${API_BASE}/${todo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: todo.title, done: !todo.done }),
      });

      if (!res.ok) {
        console.error('toggleDone failed', res.status);
        return;
      }

      const updated = await res.json();
      setTodos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err) {
      console.error('toggleDone error', err);
    }
  }

  async function removeTodo(id) {
    try {
      const res = await fetch(`${API_BASE}/${id}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        console.error('removeTodo failed', res.status);
        return;
      }

      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error('removeTodo error', err);
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simple Todos (React + FastAPI + Mongo)</h1>

        <form onSubmit={addTodo} style={{ marginBottom: 12 }}>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="New todo title"
            style={{ padding: 8, width: 300 }}
          />
          <button style={{ marginLeft: 8, padding: '8px 12px' }}>Add</button>
        </form>

        <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
          <button onClick={fetchSampleTodos} style={{ padding: '8px 12px' }}>
            Load sample todos (health check)
          </button>
          <button onClick={fetchTodos} style={{ padding: '8px 12px' }}>
            Load todos from backend
          </button>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, width: 480 }}>
            {todos.length === 0 && <li>No todos yet.</li>}
            {todos.map((todo) => (
              <li
                key={todo.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginBottom: 8,
                }}
              >
                <input
                  type="checkbox"
                  checked={!!todo.done}
                  onChange={() => toggleDone(todo)}
                />
                <span
                  style={{
                    marginLeft: 8,
                    flex: 1,
                    textDecoration: todo.done ? 'line-through' : 'none',
                  }}
                >
                  {todo.title}
                </span>
                <button
                  onClick={() => removeTodo(todo.id)}
                  style={{ marginLeft: 8 }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}

        <p style={{ marginTop: 18, fontSize: 12, opacity: 0.8 }}>
          This UI talks to <code>/api/todos</code>.
        </p>
      </header>
    </div>
  );
}

export default App;
