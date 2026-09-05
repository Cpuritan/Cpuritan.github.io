import assert from "node:assert/strict";
import test from "node:test";
import worker from "./index.js";

class MemoryKv {
  values = new Map();

  async get(key, options) {
    const value = this.values.get(key);
    if (value === undefined) return null;
    return options?.type === "json" ? JSON.parse(value) : value;
  }

  async put(key, value) {
    this.values.set(key, value);
  }
}

test("GET /api/quotas returns stored quota snapshots", async () => {
  const kv = new MemoryKv();
  await kv.put("quota:kimi", JSON.stringify({ capturedAt: "2026-09-05T12:00:00Z", accounts: [] }));
  const response = await worker.fetch(new Request("https://example.com/api/quotas"), { QUOTA_USAGE: kv });
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.kimi.capturedAt, "2026-09-05T12:00:00Z");
  assert.equal(body.codex, null);
});

test("POST /api/quotas/codex requires the push token", async () => {
  const response = await worker.fetch(new Request("https://example.com/api/quotas/codex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  }), {
    QUOTA_USAGE: new MemoryKv(),
    QUOTA_PUSH_TOKEN: "push-secret",
  });

  assert.equal(response.status, 401);
});

test("POST /api/quotas/codex stores a sanitized snapshot", async () => {
  const kv = new MemoryKv();
  const payload = {
    capturedAt: "2026-09-05T12:00:00Z",
    fiveHour: { remainingPercent: 40, resetsAt: "2026-09-05T14:00:00Z" },
    weekly: { remainingPercent: 75, resetsAt: "2026-09-08T14:00:00Z" },
  };
  const response = await worker.fetch(new Request("https://example.com/api/quotas/codex", {
    method: "POST",
    headers: {
      Authorization: "Bearer push-secret",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }), {
    QUOTA_USAGE: kv,
    QUOTA_PUSH_TOKEN: "push-secret",
  });

  assert.equal(response.status, 200);
  assert.deepEqual(JSON.parse(kv.values.get("quota:codex")), {
    capturedAt: "2026-09-05T12:00:00.000Z",
    fiveHour: { remainingPercent: 40, resetsAt: "2026-09-05T14:00:00.000Z" },
    weekly: { remainingPercent: 75, resetsAt: "2026-09-08T14:00:00.000Z" },
  });
});

test("POST /api/quotas/kimi stores only the two public account snapshots", async () => {
  const kv = new MemoryKv();
  const payload = {
    capturedAt: "2026-09-05T12:00:00Z",
    accounts: [
      {
        name: "Kimi-Bob",
        privateField: "discarded",
        fiveHour: { remainingPercent: 96, resetsAt: "2026-09-05T13:00:00Z" },
        weekly: { remainingPercent: 84, resetsAt: "2026-09-08T08:00:00Z" },
      },
      {
        name: "Kimi-Mary",
        fiveHour: { remainingPercent: 91, resetsAt: "2026-09-05T14:00:00Z" },
        weekly: { remainingPercent: 72, resetsAt: "2026-09-09T08:00:00Z" },
      },
    ],
  };
  const response = await worker.fetch(new Request("https://example.com/api/quotas/kimi", {
    method: "POST",
    headers: {
      Authorization: "Bearer push-secret",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }), {
    QUOTA_USAGE: kv,
    QUOTA_PUSH_TOKEN: "push-secret",
  });

  const stored = kv.values.get("quota:kimi");
  assert.equal(response.status, 200);
  assert.equal(JSON.parse(stored).accounts.length, 2);
  assert.equal(stored.includes("privateField"), false);
});
