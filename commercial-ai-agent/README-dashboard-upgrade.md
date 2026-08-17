Dashboard upgrade notes

- Backend: new blueprint at backend/api/dashboard.py exposing /api/clients, /api/services, /api/quotes, /api/invoices endpoints.
- Frontend: scaffold at frontend/dashboard (React + Vite + Tailwind). Use npm install then npm run dev.
- The backend app registers the blueprint automatically if present; add migrations (alembic) if models changed.
- Authentication: frontend stores JWT in localStorage and attaches it to requests.
