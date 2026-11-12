import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [message, setMessage] = useState('Connecting to the API…');
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    async function loadMessage() {
      try {
        const response = await fetch('/api/message', { signal: controller.signal });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const data = await response.json();
        setMessage(data.message);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(true);
          setMessage('Unable to reach the API. Please try again later.');
        }
      }
    }
    loadMessage();
    return () => controller.abort();
  }, []);

  return (
    <main>
      <p className="eyebrow">AI/MLops Hands-On</p>
      <h1>Your application starts here.</h1>
      <p>React frontend · Nginx gateway · FastAPI backend</p>
      <section aria-live="polite" className={error ? 'status error' : 'status'}>
        {message}
      </section>
      <a href="/api/docs">Explore the API documentation →</a>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
