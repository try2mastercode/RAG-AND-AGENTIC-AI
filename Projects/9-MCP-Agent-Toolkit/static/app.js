// Plain JS, no build step. Talks to the FastAPI backend on the same origin.

const els = {
  messages: document.getElementById("messages"),
  empty: document.getElementById("empty-state"),
  form: document.getElementById("composer"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  taskList: document.getElementById("task-list"),
  tasksEmpty: document.getElementById("tasks-empty"),
  taskCount: document.getElementById("task-count"),
  noteList: document.getElementById("note-list"),
  notesEmpty: document.getElementById("notes-empty"),
  newChat: document.getElementById("new-chat"),
  planDay: document.getElementById("plan-day"),
  inspector: document.getElementById("chat-inspector"),
  protoTools: document.getElementById("proto-tools"),
  protoResources: document.getElementById("proto-resources"),
  protoPrompts: document.getElementById("proto-prompts"),
};

// One thread_id = one conversation kept server-side in memory.
function getThreadId() {
  let id = localStorage.getItem("thread_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("thread_id", id);
  }
  return id;
}
let threadId = getThreadId();

// ---------- SECTION 1: PROTOCOL INSPECTOR (what GET /protocol reports) ----------
async function loadProtocol() {
  const res = await fetch("/protocol");
  const data = await res.json();

  els.protoTools.replaceChildren(
    ...data.tools.map((t) => listItem(t.name, t.description))
  );
  els.protoResources.replaceChildren(
    ...data.resources.map((r) => listItem(r.uri, r.description))
  );
  els.protoPrompts.replaceChildren(
    ...data.prompts.map((p) => listItem(p.name, p.description))
  );
}

function listItem(name, desc) {
  const li = document.createElement("li");
  const n = document.createElement("div");
  n.className = "name";
  n.textContent = name;
  const d = document.createElement("div");
  d.className = "desc";
  d.textContent = desc || "";
  li.append(n, d);
  return li;
}

// ---------- SECTION 2: CHAT RENDERING ----------
function addMessage(text, kind) {
  els.empty.hidden = true;
  const li = document.createElement("li");
  li.className = `msg ${kind}`;
  li.textContent = text; // textContent, never innerHTML: model output is untrusted
  els.messages.appendChild(li);
  li.scrollIntoView({ block: "end" });
  return li;
}

function showTrace(trace) {
  if (!trace || !trace.length) return;
  const pre = els.inspector.querySelector("pre");
  pre.textContent = trace
    .map(
      (step, i) =>
        `[${i + 1}] session.call_tool("${step.tool}", ${JSON.stringify(step.arguments)})\n` +
        `    -> ${JSON.stringify(step.result)}`
    )
    .join("\n\n");
  els.inspector.hidden = false;
  els.inspector.open = true;
}

// ---------- SECTION 3: SIDEBAR (tasks + notes, read via /tasks and /notes) ----------
function renderTasks(tasks) {
  els.taskList.replaceChildren();
  els.tasksEmpty.hidden = tasks.length > 0;
  const pending = tasks.filter((t) => !t.done).length;
  els.taskCount.textContent = tasks.length ? `${pending} pending` : "";

  for (const task of tasks.sort((a, b) => b.id - a.id)) {
    const li = document.createElement("li");
    li.className = `item ${task.done ? "done" : task.priority}`;
    const title = document.createElement("div");
    title.className = "title";
    title.textContent = task.title;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = [`#${task.id}`, task.priority, task.due_date || "no date"].join(" · ");
    li.append(title, meta);
    els.taskList.appendChild(li);
  }
}

function renderNotes(notes) {
  els.noteList.replaceChildren();
  els.notesEmpty.hidden = notes.length > 0;
  for (const note of notes) {
    const li = document.createElement("li");
    li.className = "item";
    const title = document.createElement("div");
    title.className = "title";
    title.textContent = note.title;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = note.tags || "no tags";
    li.append(title, meta);
    els.noteList.appendChild(li);
  }
}

async function refreshSidebar() {
  const [tasks, notes] = await Promise.all([
    fetch("/tasks").then((r) => r.json()),
    fetch("/notes").then((r) => r.json()),
  ]);
  renderTasks(tasks);
  renderNotes(notes);
}

// ---------- SECTION 4: NETWORK ----------
async function send(url, body) {
  setBusy(true);
  const thinking = addMessage("Thinking…", "bot thinking");
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    thinking.remove();
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
    if (data.reply) addMessage(data.reply, "bot");
    showTrace(data.trace);
    await refreshSidebar();
  } catch (err) {
    thinking.remove();
    addMessage(err.message || "Can't reach the server. Check that uvicorn is running.", "error");
  } finally {
    setBusy(false);
  }
}

function setBusy(busy) {
  els.send.disabled = busy;
  els.input.disabled = busy;
  if (!busy) els.input.focus();
}

// ---------- SECTION 5: EVENTS ----------
els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = els.input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  els.input.value = "";
  autoGrow();
  send("/chat", { thread_id: threadId, message: text });
});

// Enter sends, Shift+Enter makes a new line
els.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    els.form.requestSubmit();
  }
});

function autoGrow() {
  els.input.style.height = "auto";
  els.input.style.height = `${els.input.scrollHeight}px`;
}
els.input.addEventListener("input", autoGrow);

document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => {
    els.input.value = chip.textContent;
    els.form.requestSubmit();
  })
);

els.planDay.addEventListener("click", () => {
  addMessage("Plan my day", "user");
  send("/plan", { thread_id: threadId, message: "plan my day" });
});

els.newChat.addEventListener("click", async () => {
  await fetch(`/chat/${threadId}/reset`, { method: "POST" });
  localStorage.removeItem("thread_id");
  threadId = getThreadId();
  els.messages.replaceChildren(els.empty);
  els.empty.hidden = false;
  els.inspector.hidden = true;
  els.input.focus();
});

loadProtocol();
refreshSidebar();
