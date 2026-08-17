# Commercial Dashboard (frontend)

Quick scaffold for the dashboard UI (Vite + React + Tailwind).

Run locally:

1. cd frontend/dashboard-app
2. npm install
3. npm run dev

By default the frontend expects the backend at http://localhost:5000 (set VITE_API_BASE to change).

This scaffold contains placeholder pages: Dashboard, Clients, Quotes, Assignments. Implement routing and forms as needed.

Approvals
-------
The approvals page lists pending toolcalls and allows ADMIN/SALES users to approve queued toolcalls (document generation, email send). Login with a user that has ADMIN or SALES role. The scaffold uses /api endpoints on the backend.
