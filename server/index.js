import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import { readFileSync } from "node:fs";

// Load .env if present (lets us avoid a `dotenv` dependency).
// Never overrides process.env values that were set on the command line —
// those always win, so servers can be re-pinned ad-hoc.
try {
  const envPath = path.join(import.meta.dirname, ".env");
  const raw = readFileSync(envPath, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    if (process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
} catch {
  // .env missing — fine, fall back to real env vars.
}

const PORT = Number(process.env.PORT ?? 3010);
const DATA_DIR = path.resolve(process.env.DATA_DIR ?? path.join(import.meta.dirname, "..", "src", "data"));
const DATA_FILE = path.join(DATA_DIR, "schedule.json");

// NOTE: Authentication has been removed entirely — login is now handled
// purely on the client side (Q&A in the browser sessionStorage). This
// server is only used during local `astro dev` (Vite proxy on port 4321 ->
// 3010); it's never exposed to the public internet. Anyone who can reach
// this loopback server can already read/write your source files, so the
// previous JWT/cookie auth provided no real protection here.

const app = express();
app.use(express.json({ limit: "1mb" }));

// ---- helpers ---------------------------------------------------------------

async function readSchedule() {
  try {
    const text = await fs.readFile(DATA_FILE, "utf8");
    return JSON.parse(text);
  } catch (err) {
    if (err.code === "ENOENT") return {};
    throw err;
  }
}

async function writeSchedule(data) {
  const tmp = DATA_FILE + ".tmp-" + process.pid;
  await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
  await fs.writeFile(tmp, JSON.stringify(data, null, 2) + "\n", "utf8");
  await fs.rename(tmp, DATA_FILE);
}

/** Validate an array of event entries (reject malformed server-side). */
function cleanEntries(entries) {
  if (!Array.isArray(entries)) return [];
  return entries.map((e) => {
    const out = {};
    if (typeof e?.time === "string" && e.time.length <= 32) out.time = e.time;
    if (typeof e?.title === "string" && e.title.length <= 200) out.title = e.title.trim();
    if (typeof e?.location === "string" && e.location.length <= 200 && e.location.trim()) out.location = e.location.trim();
    if (typeof e?.category === "string" && /^[\w-]{0,32}$/.test(e.category)) out.category = e.category;
    if (typeof e?.id === "string" && e.id.length <= 64) out.id = e.id;
    if (typeof e?.color === "string" && /^#[0-9a-fA-F]{6}$/.test(e.color)) out.color = e.color;
    if (e?.done === 0 || e?.done === 1 || e?.done === 2) out.done = e.done;
    return out;
  }).filter((e) => e.title);
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

// ---- routes ----------------------------------------------------------------

app.get("/api/health", (_, res) => res.json({ ok: true }));

app.get("/api/schedule", async (_req, res) => {
  try {
    res.json(await readSchedule());
  } catch (err) {
    console.error("[schedule] read failed:", err);
    res.status(500).json({ error: "Failed to read schedule" });
  }
});

app.post("/api/schedule/save", async (req, res) => {
  const { date, entries } = req.body ?? {};
  if (typeof date !== "string" || !DATE_RE.test(date)) {
    return res.status(400).json({ error: "Invalid date, expected YYYY-MM-DD" });
  }
  const cleaned = cleanEntries(entries);
  try {
    const data = await readSchedule();
    if (cleaned.length === 0) {
      delete data[date];
    } else {
      data[date] = cleaned;
    }
    await writeSchedule(data);
    res.json({ success: true, date, entries: cleaned });
  } catch (err) {
    console.error("[schedule] save failed:", err);
    res.status(500).json({ error: "Failed to save" });
  }
});

app.post("/api/schedule/saveAll", async (req, res) => {
  const { schedule } = req.body ?? {};
  if (typeof schedule !== "object" || schedule === null || Array.isArray(schedule)) {
    return res.status(400).json({ error: "Invalid schedule object" });
  }
  const cleaned = {};
  for (const [k, v] of Object.entries(schedule)) {
    if (k === "__periods__") {
      if (Array.isArray(v)) {
        cleaned.__periods__ = v.map(p => ({
          id: typeof p.id === "string" && p.id.length <= 64 ? p.id : "",
          title: typeof p.title === "string" ? p.title.trim() : "",
          start: typeof p.start === "string" && /^\d{4}-\d{2}-\d{2}$/.test(p.start) ? p.start : "",
          end: typeof p.end === "string" && /^\d{4}-\d{2}-\d{2}$/.test(p.end) ? p.end : "",
          time: typeof p.time === "string" && p.time.length <= 32 ? p.time : "全天",
          category: typeof p.category === "string" && /^[\w-]{0,32}$/.test(p.category) ? p.category : "other",
          color: typeof p.color === "string" && /^#[0-9a-fA-F]{6}$/.test(p.color) ? p.color : undefined,
          done: p.done === 0 || p.done === 1 || p.done === 2 ? p.done : 0,
        })).filter(p => p.id && p.start && p.end && p.title);
      }
      continue;
    }
    if (!DATE_RE.test(k)) continue;
    const arr = cleanEntries(v);
    if (arr.length) cleaned[k] = arr;
  }
  try {
    await writeSchedule(cleaned);
    res.json({ success: true, count: Object.keys(cleaned).length });
  } catch (err) {
    console.error("[schedule] saveAll failed:", err);
    res.status(500).json({ error: "Failed to save" });
  }
});

app.listen(PORT, () => {
  console.log(`[schedule] API running at http://localhost:${PORT}`);
  console.log(`[schedule] data file: ${DATA_FILE}`);
});
