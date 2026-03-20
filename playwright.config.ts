import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/ui",
  testMatch: "*.spec.ts",
  timeout: 60_000,
  workers: 1,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://127.0.0.1:8000",
    headless: true,
    trace: "retain-on-failure",
  },
  webServer: {
    command: "arch -arm64 .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
    url: "http://127.0.0.1:8000/health",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
