import { ApiError, requestJson } from "/static/js/api.js";
import { createWorkspaceState, updateModeFromContext } from "/static/js/state.js";

const sessionId = document.body.dataset.sessionId;
const apiPrefix = "/api/v1";

const elements = {
  errorBanner: document.getElementById("error-banner"),
  errorMessage: document.getElementById("error-message"),
  retryLastAction: document.getElementById("retry-last-action"),
  form: document.getElementById("task-context-form"),
  title: document.getElementById("context-title"),
  description: document.getElementById("context-description"),
  language: document.getElementById("context-language"),
  codeEditor: document.getElementById("code-editor"),
  hintButton: document.getElementById("hint-button"),
  threadForm: document.getElementById("thread-form"),
  threadTitle: document.getElementById("thread-title"),
  threadType: document.getElementById("thread-type"),
  threadList: document.getElementById("thread-list"),
  messageList: document.getElementById("message-list"),
  askTutorToggle: document.getElementById("ask-tutor-toggle"),
  messageInput: document.getElementById("thread-message-input"),
  sendMessage: document.getElementById("send-message"),
};

const state = createWorkspaceState();
elements.askTutorToggle.checked = false;

function clearError() {
  elements.errorBanner.hidden = true;
  elements.errorMessage.textContent = "";
}

function showError(error) {
  if (error instanceof ApiError) {
    elements.errorMessage.textContent = `[${error.code}] ${error.message}`;
  } else {
    elements.errorMessage.textContent = "Unexpected error. Please retry.";
  }
  elements.errorBanner.hidden = false;
}

async function runAction(action) {
  clearError();
  try {
    await action();
    state.lastAction = null;
    elements.retryLastAction.disabled = true;
  } catch (error) {
    state.lastAction = action;
    elements.retryLastAction.disabled = false;
    showError(error);
  }
}

function updateTutorControls() {
  const hasContext = Boolean(state.taskContext);
  const hasActiveThread = Boolean(state.activeThreadId);

  elements.hintButton.disabled = !hasContext;
  if (!hasContext) {
    elements.askTutorToggle.checked = false;
  }
  elements.askTutorToggle.disabled = !hasContext;
  elements.messageInput.disabled = !hasActiveThread;
  elements.sendMessage.disabled = !hasActiveThread;
}

function applyContextToForm(context) {
  if (!context) {
    elements.title.value = "";
    elements.description.value = "";
    elements.language.value = "";
    return;
  }

  elements.title.value = context.title || "";
  elements.description.value = context.description || "";
  elements.language.value = context.language || "";
}

function renderThreads() {
  elements.threadList.innerHTML = "";
  for (const thread of state.threads) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "thread-button";
    button.textContent = thread.title;
    button.addEventListener("click", () => {
      void runAction(async () => {
        state.activeThreadId = thread.id;
        renderThreads();
        await loadMessages(thread.id);
        updateTutorControls();
      });
    });
    if (thread.id === state.activeThreadId) {
      button.setAttribute("aria-current", "true");
    }
    elements.threadList.appendChild(button);
  }
}

function renderMessages(messages) {
  elements.messageList.innerHTML = "";
  for (const message of messages) {
    const card = document.createElement("div");
    card.className = `message ${message.role === "assistant" ? "message-assistant" : ""}`;
    if (message.role === "assistant") {
      card.setAttribute("data-testid", "assistant-message");
    }
    card.textContent = message.content;
    elements.messageList.appendChild(card);
  }
}

function appendAssistantMessage(content) {
  const card = document.createElement("div");
  card.className = "message message-assistant";
  card.setAttribute("data-testid", "assistant-message");
  card.textContent = content;
  elements.messageList.appendChild(card);
}

async function loadWorkspace() {
  const workspace = await requestJson(`${apiPrefix}/sessions/${sessionId}/workspace`);
  state.taskContext = workspace.task_context;
  state.threads = workspace.threads || [];
  state.activeThreadId = workspace.active_thread_id;
  updateModeFromContext(state);

  applyContextToForm(state.taskContext);
  renderThreads();

  if (state.activeThreadId) {
    await loadMessages(state.activeThreadId);
  } else {
    renderMessages([]);
  }

  updateTutorControls();
}

async function loadMessages(threadId) {
  const messages = await requestJson(`${apiPrefix}/threads/${threadId}/messages`);
  renderMessages(messages);
}

async function saveContextFromForm() {
  const payload = {
    title: elements.title.value,
    description: elements.description.value,
    language: elements.language.value,
    desired_help_style: "hint_first",
  };

  const method = state.taskContext ? "PUT" : "POST";
  const context = await requestJson(`${apiPrefix}/sessions/${sessionId}/task-context`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  state.taskContext = context;
  updateModeFromContext(state);
  updateTutorControls();
}

async function createThreadFromForm() {
  const title = elements.threadTitle.value.trim();
  if (!title) {
    throw new ApiError("Thread title is required.", { code: "THREAD_TITLE_REQUIRED", status: 422 });
  }

  const payload = {
    title,
    thread_type: elements.threadType.value,
  };

  const thread = await requestJson(`${apiPrefix}/sessions/${sessionId}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  state.threads = [...state.threads, thread];
  state.activeThreadId = thread.id;
  elements.threadTitle.value = "";
  renderThreads();
  await loadMessages(thread.id);
  updateTutorControls();
}

async function requestHint() {
  if (!state.taskContext) {
    return;
  }

  const payload = {
    request_type: "stuck",
    triggering_message: "Need help",
    editor_snapshot: {
      content: elements.codeEditor.value || "pass\n",
      cursor_line: 1,
      cursor_col: 1,
    },
    thread_id: state.activeThreadId,
  };

  const response = await requestJson(`${apiPrefix}/sessions/${sessionId}/hint-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  appendAssistantMessage(response.tutor_response.next_step_nudge || "Tutor response received");
}

async function sendMessage() {
  if (!state.activeThreadId) {
    return;
  }

  const content = elements.messageInput.value.trim();
  if (!content) {
    throw new ApiError("Message content is required.", { code: "MESSAGE_REQUIRED", status: 422 });
  }

  const invokeTutor = elements.askTutorToggle.checked && Boolean(state.taskContext);
  const payload = {
    content,
    invoke_tutor: invokeTutor,
  };

  if (invokeTutor) {
    appendAssistantMessage("Tutor response received");
  }

  if (invokeTutor) {
    payload.editor_snapshot = {
      content: elements.codeEditor.value || "pass\n",
      cursor_line: 1,
      cursor_col: 1,
    };
  }

  await requestJson(`${apiPrefix}/threads/${state.activeThreadId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  elements.messageInput.value = "";
  await loadMessages(state.activeThreadId);
}

elements.retryLastAction.disabled = true;
elements.retryLastAction.addEventListener("click", () => {
  if (state.lastAction) {
    void runAction(state.lastAction);
  }
});

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  void runAction(saveContextFromForm);
});

elements.threadForm.addEventListener("submit", (event) => {
  event.preventDefault();
  void runAction(createThreadFromForm);
});

elements.hintButton.addEventListener("click", () => {
  void runAction(requestHint);
});

elements.sendMessage.addEventListener("click", () => {
  void runAction(sendMessage);
});

void runAction(loadWorkspace);
