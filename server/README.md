# Schedule API server — cpuritan.cn

Tiny Express server for **local development only**. Provides read/write access
to `schedule.json` so that the dev server (`astro dev`) can persist edits.

> **Why no auth?** The deployed site runs on GitHub Pages (static site). There
> is no backend server available in production. Editing login is handled
> entirely on the client side via a Q&A check stored in `sessionStorage`.
> This dev-only server listens only on `localhost` and is never exposed to the
> public internet. Anyone who can reach localhost:3010 can already read the
> local filesystem — so server-side auth would be theatre here.

## Quick start

```bash
cd server
npm install
node index.js
```

The server runs on **http://localhost:3010**.

## API

### `GET /api/schedule`
Returns the full schedule object.

### `POST /api/schedule/save`
Body: `{ "date": "YYYY-MM-DD", "entries": [...] }`.
Replaces the entries for that single date.

### `POST /api/schedule/saveAll`
Body: `{ "schedule": { ... } }`.
Fully replaces the entire schedule object.

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `PORT` | `3010` | HTTP port |
| `DATA_DIR` | `../src/data` | Directory containing `schedule.json` |
