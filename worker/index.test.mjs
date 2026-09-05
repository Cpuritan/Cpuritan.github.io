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

const kimiResponse = {
  usage: { remaining: "84", resetTime: "2026-09-08T08:00:00Z" },
  limits: [{
    window: { duration: 300, timeUnit: "TIME_UNIT_MINUTE" },
    detail: { remaining: "96", resetTime: "2026-09-05T13:00:00Z" },
  }],
};

test("GET /api/quotas returns sanitized Kimi quota data", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify(kimiResponse), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });

  try {
    const response = await worker.fetch(new Request("https://example.com/api/quotas"), {
      QUOTA_USAGE: new MemoryKv(),
      KIMI_BOB_API_KEY: "bob-secret",
      KIMI_MARY_API_KEY: "mary-secret",
    });
    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.kimi.accounts.length, 2);
    assert.equal(body.kimi.accounts[0].fiveHour.remainingPercent, 96);
    assert.equal(body.kimi.accounts[0].weekly.remainingPercent, 84);
    assert.equal(JSON.stringify(body).includes("secret"), false);
  } finally {
    globalThis.fetch = originalFetch;
  }
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
