import express from "express";
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import jwt from "jsonwebtoken";
import cookieParser from "cookie-parser";

const PORT = Number(process.env.PORT ?? 3010);
const PASSWORD = process.env.PASSWORD ?? "";
const DATA_DIR = path.resolve(process.env.DATA_DIR ?? path.join(import.meta.dirname, "..", "src", "data"));
const DATA_FILE = path.join(DATA_DIR, "schedule.json");
const TOKEN_TTL = "14d";

if (!PASSWORD) {
  console.error("[schedule] FATAL: PASSWORD env var must be set.");
  console.error("           Example: PASSWORD=secret node index.js");
  process.exit(1);
}

const secret = crypto.createHash("sha256").update(PASSWORD).digest();
const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(cookieParser());

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

function requireAuth(req, res, next) {
  const token = req.cookies?.token ?? req.headers["x-auth-token"];
  if (!token) return res.status(401).json({ error: "Not authenticated" });
  try {
    jwt.verify(token, secret);
    next();
  } catch {
    return res.status(403).json({ error: "Invalid or expired token" });
  }
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

app.post("/api/login", (req, res) => {
  const { password } = req.body ?? {};
  if (typeof password !== "string" || password.length === 0) {
    return res.status(400).json({ error: "Password required" });
  }
  // constant-time compare to avoid trivial timing leaks
  const a = Buffer.from(password);
  const b = Buffer.from(PASSWORD);
  const ok = a.length === b.length && crypto.timingSafeEqual(a, b);
  if (!ok) return res.status(401).json({ error: "Wrong password" });
  const token = jwt.sign({ role: "admin" }, secret, { expiresIn: TOKEN_TTL });
  res.cookie("token", token, {
    httpOnly: true,
    sameSite: "lax",
    maxAge: 14 * 24 * 60 * 60 * 1000,
    // secure: true,  // enable in production behind HTTPS
  });
  res.json({ success: true });
});

app.post("/api/logout", (_req, res) => {
  res.clearCookie("token");
  res.json({ success: true });
});

app.get("/api/auth/check", requireAuth, (_req, res) => {
  res.json({ authenticated: true });
});

app.post("/api/schedule/save", requireAuth, async (req, res) => {
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

app.post("/api/schedule/saveAll", requireAuth, async (req, res) => {
  const { schedule } = req.body ?? {};
  if (typeof schedule !== "object" || schedule === null || Array.isArray(schedule)) {
    return res.status(400).json({ error: "Invalid schedule object" });
  }
  const cleaned = {};
  for (const [k, v] of Object.entries(schedule)) {
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
