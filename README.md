# NFL App

NFL App is an interactive NFL data explorer built with a React frontend and a Flask backend.

It lets you:
- Browse games across multiple seasons
- Filter by all games, primetime games, playoff games, divisional games, team-specific views, and head-to-head matchups
- Open individual games to view drive-based field visualizations
- Compare game-level team stats such as yards, EPA, success rate, red zone efficiency, turnovers, sacks allowed, fourth down rate, and explosive plays
- View win probability charts for selected games
- Explore offensive, defensive, and overall team rankings by season

The app is built to make it easier to compare teams, study specific games, and visually explore NFL data.

## Tech Stack

- Frontend: React + Vite + Tailwind CSS
- Backend: Flask
- Data: `nflreadpy`, `pandas`, and `numpy`

## Setup

Prerequisites:

- Node.js and npm
- Conda
- Python 3.10 in the `nfl` environment

Install frontend dependencies from the project root:

```bash
npm install
```

Activate the backend Conda environment:

```bash
conda activate nfl
```

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Run Locally

Start the Flask API on port `5001`:

```bash
conda activate nfl
cd backend
python3.10 app.py
```

You can also start the backend from the project root with:

```bash
npm run dev:backend
```

In a second terminal, start the frontend:

```bash
npm run dev:frontend
```

The app will be available at `http://127.0.0.1:5173`.

By default, Vite proxies `/api` requests to `http://127.0.0.1:5001`. If your backend runs somewhere else, set `VITE_API_BASE` before starting the frontend.

## Available Commands

From the project root:

```bash
npm run dev
npm run dev:frontend
npm run dev:backend
npm run build
npm run preview
```

- `npm run dev` starts the Vite frontend
- `npm run dev:frontend` starts the Vite frontend
- `npm run dev:backend` starts the Flask backend
- `npm run build` creates a production frontend build
- `npm run preview` previews the production frontend build locally
