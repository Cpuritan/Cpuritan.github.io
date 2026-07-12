/** Cloudflare Worker — schedule proxy for cpuritan.cn */

const REPO = { owner: "Cpuritan", name: "Cpuritan.github.io", path: "src/data/schedule.json", branch: "main" };

const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };

function ok(body) {
  return new Response(JSON.stringify(body), { status: 200, headers: { ...CORS, "Content-Type": "application/json; charset=utf-8" } });
}
function fail(status, msg) {
  return new Response(JSON.stringify({ error: msg }), { status, headers: { ...CORS, "Content-Type": "application/json; charset=utf-8" } });
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
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (!env.GH_TOKEN) return fail(500, "Worker missing GH_TOKEN secret");

    const url = new URL(req.url);
    try {
      // health
      if (url.pathname === "/api/health") return ok({ ok: true });

      // GET schedule
      if (url.pathname === "/api/schedule" && req.method === "GET") {
        const { content } = await ghGet(env.GH_TOKEN, env);
        return ok(content);
      }

      // Save single date
      if (url.pathname === "/api/schedule/save" && req.method === "POST") {
        const { date, entries } = await req.json();
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return fail(400, "Invalid date");
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        const arr = Array.isArray(entries) ? entries : [];
        if (arr.length === 0) delete content[date]; else content[date] = arr;
        await ghPut(env.GH_TOKEN, env, content, sha, `schedule: update ${date}`);
        return ok({ success: true, date });
      }

      // Save all
      if (url.pathname === "/api/schedule/saveAll" && req.method === "POST") {
        const { schedule } = await req.json();
        if (typeof schedule !== "object" || !schedule) return fail(400, "Invalid schedule object");
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        for (const [k, v] of Object.entries(schedule)) {
          if (k === "__periods__" || /^\d{4}-\d{2}-\d{2}$/.test(k)) content[k] = v;
        }
        await ghPut(env.GH_TOKEN, env, content, sha, "schedule: bulk update");
        return ok({ success: true });
      }

      return fail(404, "Not found");
    } catch (err) {
      return fail(500, err?.message || "Worker error");
    }
  },
};
