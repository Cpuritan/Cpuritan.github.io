const API_URL = "https://cpuritan-schedule.bqf-cpuritan.workers.dev/api/quotas/codex";

const [fiveHourRemaining, fiveHourResetsAt, weeklyRemaining, weeklyResetsAt] = process.argv.slice(2);
const token = process.env.CPURITAN_QUOTA_PUSH_TOKEN;

if (!token) throw new Error("Missing CPURITAN_QUOTA_PUSH_TOKEN");

const payload = {
  capturedAt: new Date().toISOString(),
  fiveHour: {
    remainingPercent: Number(fiveHourRemaining),
    resetsAt: new Date(fiveHourResetsAt).toISOString(),
  },
  weekly: {
    remainingPercent: Number(weeklyRemaining),
    resetsAt: new Date(weeklyResetsAt).toISOString(),
  },
};

if (!Number.isFinite(payload.fiveHour.remainingPercent) || !Number.isFinite(payload.weekly.remainingPercent)) {
  throw new Error("Quota percentages must be numbers");
}

const response = await fetch(API_URL, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(payload),
});

if (!response.ok) throw new Error(`Quota push failed with HTTP ${response.status}`);

console.log(`Codex quota snapshot pushed at ${payload.capturedAt}`);
