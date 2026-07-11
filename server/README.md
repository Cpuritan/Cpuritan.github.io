# Schedule API server — cpuritan.cn

Tiny Express server that provides online editing of the calendar schedule.

## Quick start

```bash
cd server
npm install
PASSWORD=mysecret node index.js          # Linux / macOS
set PASSWORD=mysecret && node index.js   # Windows cmd
$env:PASSWORD="mysecret"; node index.js  # PowerShell
```

The server runs on **http://localhost:3010**.

## How the auth works

- POST `/api/login` with `{ password }` — compares against `PASSWORD` env var.
- Returns a signed JWT cookie (expires 14 days).
- All schedule-editing endpoints require this cookie.
- The JWT secret is derived from `PASSWORD`, so a restart invalidates old tokens.

## API

### `GET /api/schedule`
Returns the full schedule object. No auth required (read-only is public).

### `POST /api/login`
Body: `{ "password": "..." }`. Returns `{ success: true, token }` + sets cookie.

### `POST /api/logout`
Clears the auth cookie.

### `POST /api/schedule/save`
Requires JWT cookie. Body: `{ "date": "YYYY-MM-DD", "entries": [...] }`.
Replaces the entries for that single date.

### `POST /api/schedule/saveAll`
Requires JWT cookie. Body: `{ "schedule": { ... } }`.
Fully replaces the entire schedule object.

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `PORT` | `3010` | HTTP port |
| `PASSWORD` | _(required)_ | Admin password for login |
| `DATA_DIR` | `../src/data` | Directory containing `schedule.json` |

## Production deployment

Deploy alongside the static site behind a reverse proxy:

```nginx
# nginx snippet
location /api/ {
    proxy_pass http://localhost:3010;
}
```

The Astro build outputs static files under `dist/`; the schedule page JS
will call `/api/schedule` (same origin) to fetch the latest schedule.
