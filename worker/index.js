/** Cloudflare Worker — schedule proxy for cpuritan.cn */

const REPO = { owner: "Cpuritan", name: "Cpuritan.github.io", path: "src/data/schedule.json", branch: "main" };

// CORS: open to all origins. The frontend uses `credentials: "omit"`, so
// `Access-Control-Allow-Origin: *` is sufficient and avoids the origin echo
// + Allow-Credentials dance that previously broke POSTs.
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
};

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, "Content-Type": "application/json; charset=utf-8" },
  });
}

// UTF-8 safe base64 helpers — required because atob/btoa operate on
// Latin-1 and corrupt any non-ASCII characters. The previous implementation
// round-tripped UTF-8 through Latin-1 twice and turned 中文 -> mojibake.
const enc = new TextEncoder();
const dec = new TextDecoder();
function b64encode(str) {
  const bytes = enc.encode(str);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
function b64decode(b64) {
  const bin = atob(b64.replace(/\n/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return dec.decode(bytes);
}

async function ghGet(token, env) {
  const o = env.GH_REPO_OWNER || REPO.owner, n = env.GH_REPO_NAME || REPO.name;
  const p = env.GH_FILE_PATH || REPO.path, b = env.GH_BRANCH || REPO.branch;
  const url = `https://api.github.com/repos/${o}/${n}/contents/${encodeURIComponent(p)}?ref=${encodeURIComponent(b)}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "User-Agent": "cpuritan-schedule" } });
  if (res.status === 404) return { sha: null, content: {} };
  if (!res.ok) { const t = await res.text().catch(() => ""); throw new Error(`GitHub GET fail: ${res.status} ${t}`); }
  const d = await res.json();
  return { sha: d.sha, content: JSON.parse(b64decode(d.content)) };
}

async function ghPut(token, env, content, sha, msg) {
  const o = env.GH_REPO_OWNER || REPO.owner, n = env.GH_REPO_NAME || REPO.name;
  const p = env.GH_FILE_PATH || REPO.path, b = env.GH_BRANCH || REPO.branch;
  const url = `https://api.github.com/repos/${o}/${n}/contents/${encodeURIComponent(p)}`;
  const payload = {
    message: msg, branch: b,
    content: b64encode(JSON.stringify(content, null, 2) + "\n"),
    ...(sha ? { sha } : {}),
  };
  const res = await fetch(url, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "User-Agent": "cpuritan-schedule", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) { const t = await res.text().catch(() => ""); throw new Error(`GitHub PUT fail: ${res.status} ${t}`); }
  return res.json();
}

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    if (!env.GH_TOKEN) return jsonResponse({ error: "Worker missing GH_TOKEN secret" }, 500);

    const url = new URL(req.url);
    try {
      if (url.pathname === "/api/health") return jsonResponse({ ok: true });

      if (url.pathname === "/api/schedule" && req.method === "GET") {
        const { content } = await ghGet(env.GH_TOKEN, env);
        return jsonResponse(content);
      }

      if (url.pathname === "/api/schedule/save" && req.method === "POST") {
        const { date, entries } = await req.json();
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return jsonResponse({ error: "Invalid date" }, 400);
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        const arr = Array.isArray(entries) ? entries : [];
        if (arr.length === 0) delete content[date]; else content[date] = arr;
        await ghPut(env.GH_TOKEN, env, content, sha, `schedule: update ${date}`);
        return jsonResponse({ success: true, date });
      }

      if (url.pathname === "/api/schedule/saveAll" && req.method === "POST") {
        const { schedule } = await req.json();
        if (typeof schedule !== "object" || !schedule) return jsonResponse({ error: "Invalid schedule object" }, 400);
        const { sha, content } = await ghGet(env.GH_TOKEN, env);
        for (const [k, v] of Object.entries(schedule)) {
          if (k === "__periods__" || /^\d{4}-\d{2}-\d{2}$/.test(k)) content[k] = v;
        }
        await ghPut(env.GH_TOKEN, env, content, sha, "schedule: bulk update");
        return jsonResponse({ success: true });
      }

      return jsonResponse({ error: "Not found" }, 404);
    } catch (err) {
      return jsonResponse({ error: err?.message || "Worker error" }, 500);
    }
  },
};
