const sessionId = document.body.dataset.sessionId;
const apiPrefix = "/api/v1";

const elements = {
  form: document.getElementById("task-context-form"),
  title: document.getElementById("context-title"),
  description: document.getElementById("context-description"),
  language: document.getElementById("context-language"),
  codeEditor: document.getElementById("code-editor"),
  hintButton: document.getElementById("hint-button"),
  threadList: document.getElementById("thread-list"),
  messageList: document.getElementById("message-list"),
  askTutorToggle: document.getElementById("ask-tutor-toggle"),
  messageInput: document.getElementById("thread-message-input"),
  sendMessage: document.getElementById("send-message"),
};

const state = {
  taskContext: null,
  threads: [],
  activeThreadId: null,
};

elements.askTutorToggle.checked = false;

function renderThreads() {
  elements.threadList.innerHTML = "";
  for (const thread of state.threads) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "thread-button";
    button.textContent = thread.title;
    button.addEventListener("click", () => {
      state.activeThreadId = thread.id;
      loadMessages(thread.id);
    });
    elements.threadList.appendChild(button);
  }
}

function renderMessages(messages) {
  elements.messageList.innerHTML = "";
  for (const message of messages) {
    const card = document.createElement("div");
    card.className = `message ${message.role === "assistant" ? "message-assistant" : ""}`;
    if (message.role === "assistant") {
      card.dataset.testid = "assistant-message";
      card.setAttribute("data-testid", "assistant-message");
    }
    card.textContent = message.content;
    elements.messageList.appendChild(card);
  }
}

function appendAssistantMessage(content) {
  const card = document.createElement("div");
  card.className = "message message-assistant";
  card.dataset.testid = "assistant-message";
  card.setAttribute("data-testid", "assistant-message");
  card.textContent = content;
  elements.messageList.appendChild(card);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error?.message || "Request failed");
  }
  return data;
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

async function loadWorkspace() {
  const workspace = await fetchJson(`${apiPrefix}/sessions/${sessionId}/workspace`);
  state.taskContext = workspace.task_context;
  state.threads = workspace.threads || [];
  state.activeThreadId = workspace.active_thread_id;

  applyContextToForm(state.taskContext);
  elements.hintButton.disabled = !state.taskContext;

  renderThreads();

  if (state.activeThreadId) {
    await loadMessages(state.activeThreadId);
  } else {
    renderMessages([]);
  }
}

async function loadMessages(threadId) {
  const messages = await fetchJson(`${apiPrefix}/threads/${threadId}/messages`);
  renderMessages(messages);
}

async function saveContext(event) {
  event.preventDefault();

  const payload = {
    title: elements.title.value,
    description: elements.description.value,
    language: elements.language.value,
    desired_help_style: "hint_first",
  };

  const method = state.taskContext ? "PUT" : "POST";
  const context = await fetchJson(`${apiPrefix}/sessions/${sessionId}/task-context`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  state.taskContext = context;
  elements.hintButton.disabled = false;
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

  const response = await fetchJson(`${apiPrefix}/sessions/${sessionId}/hint-requests`, {
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

  const invokeTutor = elements.askTutorToggle.checked;
  const payload = {
    content: elements.messageInput.value,
    invoke_tutor: invokeTutor,
  };

  if (invokeTutor) {
    payload.editor_snapshot = {
      content: elements.codeEditor.value || "pass\n",
      cursor_line: 1,
      cursor_col: 1,
    };
  }

  await fetchJson(`${apiPrefix}/threads/${state.activeThreadId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  elements.messageInput.value = "";
  await loadMessages(state.activeThreadId);
}

elements.form.addEventListener("submit", saveContext);
elements.hintButton.addEventListener("click", requestHint);
elements.sendMessage.addEventListener("click", sendMessage);

loadWorkspace();
