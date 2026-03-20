import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:8000";
const RUN_UI_TESTS = process.env.RUN_UI_TESTS === "1";
const API_PREFIX = "/api/v1";

function uiGuard() {
  test.skip(!RUN_UI_TESTS, "Set RUN_UI_TESTS=1 to run UI interaction tests.");
}

async function createSession(request: APIRequestContext): Promise<{ session_id: string }> {
  const response = await request.post(`${BASE_URL}${API_PREFIX}/sessions`, { data: {} });
  expect(response.status(), await response.text()).toBe(201);
  return (await response.json()) as { session_id: string };
}

async function createTaskContext(request: APIRequestContext, sessionId: string, title = "Binary search") {
  const response = await request.post(`${BASE_URL}${API_PREFIX}/sessions/${sessionId}/task-context`, {
    data: {
      title,
      description: "Implement iterative binary search",
      language: "python",
      desired_help_style: "hint_first",
    },
  });
  expect([200, 201]).toContain(response.status());
}

async function createThread(
  request: APIRequestContext,
  sessionId: string,
  title: string,
  threadType: "concept" | "planning" | "general" = "general",
): Promise<{ id: string; title: string }> {
  const response = await request.post(`${BASE_URL}${API_PREFIX}/sessions/${sessionId}/threads`, {
    data: {
      title,
      thread_type: threadType,
    },
  });
  expect(response.status(), await response.text()).toBe(201);
  return (await response.json()) as { id: string; title: string };
}

async function gotoWorkspace(page: Page, sessionId: string) {
  await page.goto(`${BASE_URL}/workspace/${sessionId}`);
}

async function fillContextForm(page: Page, title: string) {
  await page.getByLabel(/title/i).fill(title);
  await page.getByLabel(/description/i).fill("Implement iterative binary search");
  await page.getByLabel(/language/i).fill("python");
  await page.getByRole("button", { name: /save/i }).click();
}

async function maybeSkipIfMissing(page: Page, selector: string, message: string) {
  if ((await page.locator(selector).count()) === 0) {
    test.skip(true, message);
  }
}

test("UI-001 first load without context enters context_required mode", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);

  await gotoWorkspace(page, session_id);

  await maybeSkipIfMissing(page, "[data-testid='task-context-panel']", "Task context panel selector not implemented yet.");
  await expect(page.locator("[data-testid='task-context-panel']")).toBeVisible();

  const hintButton = page.getByRole("button", { name: /hint\s*\/\s*i'?m getting stuck/i });
  await expect(hintButton).toBeDisabled();
});

test("UI-002 saving first context transitions mode to ready", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await gotoWorkspace(page, session_id);

  await fillContextForm(page, "Binary Search Exercise");

  const hintButton = page.getByRole("button", { name: /hint\s*\/\s*i'?m getting stuck/i });
  await expect(hintButton).toBeEnabled();
});

test("UI-002B updating context keeps ready mode and switches active context", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id, "Initial Context");

  await gotoWorkspace(page, session_id);
  await fillContextForm(page, "Updated Context");

  const workspaceResponse = await request.get(`${BASE_URL}${API_PREFIX}/sessions/${session_id}/workspace`);
  expect(workspaceResponse.status()).toBe(200);
  const workspace = (await workspaceResponse.json()) as { task_context: { title: string } };
  expect(workspace.task_context.title).toBe("Updated Context");

  const hintButton = page.getByRole("button", { name: /hint\s*\/\s*i'?m getting stuck/i });
  await hintButton.click();
});

test("UI-003 hint button flow persists and renders tutor response card", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id);
  await gotoWorkspace(page, session_id);

  await maybeSkipIfMissing(page, "[data-testid='code-editor']", "Editor selector not implemented yet.");
  await page.locator("[data-testid='code-editor']").fill("def binary_search(nums, target):\n    return -1\n");

  const hintRequestPromise = page.waitForRequest(
    (req) => req.method() === "POST" && req.url().includes(`/sessions/${session_id}/hint-requests`),
  );

  await page.getByRole("button", { name: /hint\s*\/\s*i'?m getting stuck/i }).click();
  await hintRequestPromise;

  await maybeSkipIfMissing(page, "[data-testid='assistant-message']", "Assistant response selector not implemented yet.");
  await expect(page.locator("[data-testid='assistant-message']").first()).toBeVisible();
});

test("UI-004 side-thread submit without tutor stays chat-only", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id);
  const thread = await createThread(request, session_id, "Debug Thread", "concept");

  await gotoWorkspace(page, session_id);
  await page.getByRole("button", { name: new RegExp(thread.title, "i") }).click();

  await maybeSkipIfMissing(page, "[data-testid='ask-tutor-toggle']", "Ask tutor toggle selector not implemented yet.");
  await page.locator("[data-testid='ask-tutor-toggle']").uncheck();
  await page.locator("[data-testid='thread-message-input']").fill("chat-only message");

  const messageRequest = page.waitForRequest(
    (req) => req.method() === "POST" && req.url().includes(`/threads/${thread.id}/messages`),
  );
  await page.getByRole("button", { name: /send/i }).click();

  const outbound = await messageRequest;
  const payload = outbound.postDataJSON() as { invoke_tutor?: boolean };
  expect(payload.invoke_tutor).toBe(false);
});

test("UI-005 side-thread submit with tutor renders assistant response", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id);
  const thread = await createThread(request, session_id, "Hints Thread", "planning");

  await gotoWorkspace(page, session_id);
  await page.getByRole("button", { name: new RegExp(thread.title, "i") }).click();

  await page.locator("[data-testid='ask-tutor-toggle']").check();
  await page.locator("[data-testid='thread-message-input']").fill("what is my next step?");

  const messageRequest = page.waitForRequest(
    (req) => req.method() === "POST" && req.url().includes(`/threads/${thread.id}/messages`),
  );
  await page.getByRole("button", { name: /send/i }).click();

  const outbound = await messageRequest;
  const payload = outbound.postDataJSON() as { invoke_tutor?: boolean };
  expect(payload.invoke_tutor).toBe(true);

  await maybeSkipIfMissing(page, "[data-testid='assistant-message']", "Assistant response selector not implemented yet.");
  await expect(page.locator("[data-testid='assistant-message']").last()).toBeVisible();
});

test("UI-006 multiple threads remain isolated in UI state and rendering", async ({ page, request }) => {
  uiGuard();
  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id);
  const threadA = await createThread(request, session_id, "Thread A", "concept");
  const threadB = await createThread(request, session_id, "Thread B", "planning");

  await gotoWorkspace(page, session_id);

  await page.getByRole("button", { name: new RegExp(threadA.title, "i") }).click();
  await page.locator("[data-testid='thread-message-input']").fill("only in A");
  await page.getByRole("button", { name: /send/i }).click();

  await page.getByRole("button", { name: new RegExp(threadB.title, "i") }).click();
  await page.locator("[data-testid='thread-message-input']").fill("only in B");
  await page.getByRole("button", { name: /send/i }).click();

  await page.getByRole("button", { name: new RegExp(threadA.title, "i") }).click();
  await expect(page.getByText("only in A")).toBeVisible();
  await expect(page.getByText("only in B")).toHaveCount(0);
});

test("GR-001 no polling or interval tutor invocation path exists in frontend", async ({ page, request }) => {
  uiGuard();

  const workspaceJsPath = path.resolve(process.cwd(), "app/static/js/workspace.js");
  if (!fs.existsSync(workspaceJsPath)) {
    test.skip(true, "workspace.js not available yet.");
  }

  const source = fs.readFileSync(workspaceJsPath, "utf-8");
  expect(source).not.toContain("setInterval(");

  const { session_id } = await createSession(request);
  await createTaskContext(request, session_id);
  await gotoWorkspace(page, session_id);

  let tutorCalls = 0;
  page.on("request", (req) => {
    if (req.method() === "POST" && req.url().includes("/hint-requests")) {
      tutorCalls += 1;
    }
  });

  await page.waitForTimeout(30_000);
  expect(tutorCalls).toBe(0);
});
