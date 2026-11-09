# CSAB Choice Planner Frontend

## Setup

1. Open a terminal in `frontend/`
2. Run `npm install`
3. Run `npm run dev`

If Node/npm is not installed, use the included Deno dev server instead:

1. Run `deno run --allow-net --allow-read deno_dev.ts`
2. Open `http://127.0.0.1:4173`

The app starts on `http://localhost:4173`

## Notes

- The frontend is built with React, Vite, TypeScript, and Tailwind CSS.
- API requests are proxied from `/api` to `http://127.0.0.1:8000`.
- The page structure includes:
  - `HomePage`
  - `ProfileFormPage`
  - `ResultsPage`
  - `ChoiceTable` component

## Backend connection

The frontend expects an API endpoint at `/api/recommend` that accepts a POST request with the student profile JSON and returns a recommendation result.
