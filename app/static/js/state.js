export function createWorkspaceState() {
  return {
    mode: "loading",
    taskContext: null,
    threads: [],
    activeThreadId: null,
    lastAction: null,
  };
}

export function updateModeFromContext(state) {
  state.mode = state.taskContext ? "ready" : "context_required";
}
