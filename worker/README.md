# Schedule Worker — Cloudflare Worker (deployment README)

This Cloudflare Worker proxies reads/writes from the deployed cpuritan.cn
schedule page to the GitHub Contents API, so that online edits actually
persist back to the repo (and trigger a GitHub Pages rebuild ~10s later).

The GitHub PAT lives **only** in the Worker's encrypted secret store — it
never appears in the worker bundle, never appears in the browser, and never
appears in any git-tracked file.

## One-time setup

1. **Install wrangler** (Cloudflare CLI):

   ```bash
   cd worker
   npm install
   ```

2. **Create a fine-grained GitHub PAT**:
   - GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Resource owner: `Cpuritan`
   - Repository access: Only select repositories → `Cpuritan/Cpuritan.github.io`
   - Permissions → Repository permissions → Contents: **Read and write**
   - Copy the token (starts with `github_pat_...`)

3. **Log in to Cloudflare** (creates a free account if you don't have one):

   ```bash
   npx wrangler login
   ```

4. **Set the GitHub token as a Worker secret**:

   ```bash
   npm run secret:put
   # paste the github_pat_... when prompted
   ```

5. **Deploy**:

   ```bash
   npm run deploy
   ```

   The deploy command prints a URL like:

   ```
   https://cpuritan-schedule.<your-subdomain>.workers.dev
   ```

6. **Wire the site to the Worker**: open `src/pages/schedule.astro`, change the
   `data-api` attribute on `.sched-page` to that Worker URL:

   ```astro
   <div
     class="sched-page"
     data-schedule={JSON.stringify(scheduleFallback)}
     data-today={todayStr}
     data-api="https://cpuritan-schedule.<your-subdomain>.workers.dev/api"
   >
   ```

   Rebuild + redeploy the static site (`npm run build` + `git push`) — the
   `dist/schedule/index.html` will now point to the Worker.

## Routes

| Method | Path                  | Body                          | Notes |
|--------|-----------------------|-------------------------------|-------|
| GET    | `/api/health`         | —                             | liveness |
| GET    | `/api/schedule`       | —                             | returns the JSON of schedule.json |
| POST   | `/api/schedule/save`  | `{ date, entries }`           | upsert one date |
| POST   | `/api/schedule/saveAll` | `{ schedule: {...} }`       | bulk replace (preserves unknown keys) |

## Local development

```bash
npm run dev
```

This runs the Worker locally on `http://localhost:8787` with your real
`GH_TOKEN` secret. Visit `http://localhost:8787/api/health` to verify.

## Cost

Cloudflare Workers free plan allows **100k requests per day**. A schedule page
open all day at 5-min refresh = ~290 requests/day. You're nowhere near the
limit.
