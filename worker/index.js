/** Cloudflare Worker — schedule proxy for cpuritan.cn */

const REPO = { owner: "Cpuritan", name: "Cpuritan.github.io", path: "src/data/schedule.json", branch: "main" };

// Origin allow-list — only these sites may talk to the Worker. The browser's
// CORS spec forbids `Access-Control-Allow-Origin: *` together with
// `credentials: "include"`, so we must echo the precise origin back.
const ALLOWED_ORIGINS = new Set([
  "https://cpuritan.cn",
  "https://www.cpuritan.cn",
  "http://localhost:4321", // astro dev server
  "http://127.0.0.1:4321",
  "http://localhost:3010", // direct express dev
  "http://127.0.0.1:3010",
]);

function corsHeaders(req) {
  const origin = req.headers.get("Origin") || "";
  const allowed = ALLOWED_ORIGINS.has(origin) ? origin : "";
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function jsonResponse(body, status, cors) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json; charset=utf-8" },
  });
}

async function ghGet(token, env) {
  const o = env.GH_REPO_OWNER || REPO.owner, n = env.GH_REPO_NAME || REPO.name;
  const p = env.GH_FILE_PATH || REPO.path, b = env.GH_BRANCH || REPO.branch;
  const url = `https://api.github.com/repos/${o}/${n}/contents/${encodeURIComponent(p)}?ref=${encodeURIComponent(b)}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "User-Agent": "cpuritan-schedule" } });
  if (res.status === 404) return { sha: null, content: {} };
  if (!res.ok) { const t = await res.text().catch(() => ""); throw new Error(`GitHub GET fail: ${res.status} ${t}`); }
  const d = await res.json();
  const text = atob(d.content.replace(/\n/g, ""));
  return { sha: d.sha, content: JSON.parse(text) };
}

async function ghPut(token, env, content, sha, msg) {
  const o = env.GH_REPO_OWNER || REPO.owner, n = env.GH_REPO_NAME || REPO.name;
  const p = env.GH_FILE_PATH || REPO.path, b = env.GH_BRANCH || REPO.branch;
  const url = `https://api.github.com/repos/${o}/${n}/contents/${encodeURIComponent(p)}`;
  const payload = { message: msg, branch: b, content: btoa(unescape(encodeURIComponent(JSON.stringify(content, null, 2) + "\n"))), ...(sha ? { sha } : {}) };
  const res = await fetch(url, { method: "PUT", headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "User-Agent": "cpuritan-schedule", "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!res.ok) { const t = await res.text().catch(() => ""); throw new Error(`GitHub PUT fail: ${res.status} ${t}`); }
  return res.json();
}

export default {
  async fetch(req, env) {
    const cors = corsHeaders(req);

    // CORS preflight
    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // Reject any cross-origin request from a non-allowlisted origin.
    // Same-origin (no Origin header, e.g. curl) is allowed.
    const origin = req.headers.get("Origin") || "";
    if (origin && !ALLOWED_ORIGINS.has(origin)) {
      return jsonResponse({ error: "Origin not allowed" }, 403, cors);
    }

    if (!env.GH_TOKEN) return jsonResponse({ error: "Worker missing GH_TOKEN secret" }, 500, cors);

    const url = new URL(req.url);
    try {
      if (url.pathname === "/api/health") return jsonResponse({ ok: true }, 200, cors);

      if (url.pathname === "/api/schedule" && req.method === "GET") {
        const { content } = await ghGet(env.GH_TOKEN, env);
        return jsonResponse(content, 200, cors);
      }

      if (url.pathname === "/api/schedule/save" && req.method === "POST") {
        const { date, entries } = await req.json();
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return jsonResponse({ error: "Invalid date" }, 400, cors);
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        const arr = Array.isArray(entries) ? entries : [];
        if (arr.length === 0) delete content[date]; else content[date] = arr;
        await ghPut(env.GH_TOKEN, env, content, sha, `schedule: update ${date}`);
        return jsonResponse({ success: true, date }, 200, cors);
      }

      if (url.pathname === "/api/schedule/saveAll" && req.method === "POST") {
        const { schedule } = await req.json();
        if (typeof schedule !== "object" || !schedule) return jsonResponse({ error: "Invalid schedule object" }, 400, cors);
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        for (const [k, v] of Object.entries(schedule)) {
          if (k === "__periods__" || /^\d{4}-\d{2}-\d{2}$/.test(k)) content[k] = v;
        }
        await ghPut(env.GH_TOKEN, env, content, sha, "schedule: bulk update");
        return jsonResponse({ success: true }, 200, cors);
      }

      return jsonResponse({ error: "Not found" }, 404, cors);
    } catch (err) {
      return jsonResponse({ error: err?.message || "Worker error" }, 500, cors);
    }
  },
};
