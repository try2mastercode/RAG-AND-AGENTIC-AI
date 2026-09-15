// Plain JS, no build step. Talks to the FastAPI backend on the same origin.

const API = "/api";

const els = {
  messages: document.getElementById("messages"),
  empty: document.getElementById("empty-state"),
  form: document.getElementById("composer"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  taskList: document.getElementById("task-list"),
  tasksEmpty: document.getElementById("tasks-empty"),
  taskCount: document.getElementById("task-count"),
  newChat: document.getElementById("new-chat"),
  inspector: document.getElementById("chat-inspector"),
};

// One thread_id = one conversation in the LangGraph checkpointer.
// Kept in localStorage so a page refresh continues the same conversation.
function getThreadId() {
  let id = localStorage.getItem("thread_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("thread_id", id);
  }
  return id;
}
let threadId = getThreadId();

// ---------- SECTION 1: SHARED "API INSPECTOR" HELPER ----------
async function callApi(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();

  const pre = els.inspector.querySelector("pre");
  pre.textContent = `${method} ${url}\n\nRequest body:\n${JSON.stringify(body, null, 2)}\n\nResponse (${res.status}):\n${JSON.stringify(data, null, 2)}`;
  els.inspector.hidden = false;

  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

// ---------- SECTION 2: RENDERING ----------
function addMessage(text, kind) {
  els.empty.hidden = true;
  const li = document.createElement("li");
  li.className = `msg ${kind}`;
  li.textContent = text; // textContent, never innerHTML: model output is untrusted
  els.messages.appendChild(li);
  li.scrollIntoView({ block: "end" });
  return li;
}

function addConfirm(payload) {
  const li = document.createElement("li");
  li.className = "confirm";

  const question = document.createElement("p");
  question.textContent = payload.question;

  const actions = document.createElement("div");
  actions.className = "actions";

  const yes = document.createElement("button");
  yes.className = "danger";
  yes.type = "button";
  yes.textContent = "Delete task";

  const no = document.createElement("button");
  no.className = "plain";
  no.type = "button";
  no.textContent = "Keep task";

  const answer = async (approved) => {
    if (li.classList.contains("answered")) return;
    li.classList.add("answered");
    yes.disabled = no.disabled = true;
    question.textContent += approved ? " — you chose delete." : " — you chose keep.";
    await send(`${API}/chat/resume`, { thread_id: threadId, approved });
  };
  yes.addEventListener("click", () => answer(true));
  no.addEventListener("click", () => answer(false));

  actions.append(yes, no);
  li.append(question, actions);
  els.messages.appendChild(li);
  li.scrollIntoView({ block: "end" });
  no.focus();
}

function formatDue(due) {
  if (!due) return null;
  const today = new Date().toISOString().slice(0, 10);
  const date = new Date(`${due}T00:00:00`);
  const label = date.toLocaleDateString(undefined, { day: "numeric", month: "short" });
  return { label, overdue: due < today };
}

function renderTasks(tasks) {
  els.taskList.replaceChildren();
  els.tasksEmpty.hidden = tasks.length > 0;
  const pending = tasks.filter((t) => t.status === "pending").length;
  els.taskCount.textContent = tasks.length ? `${pending} pending` : "";

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = `task ${task.priority} ${task.status}`;

    const box = document.createElement("input");
    box.type = "checkbox";
    box.checked = task.status === "done";
    box.id = `task-${task.id}`;
    box.addEventListener("change", () => toggleTask(task.id));

    const title = document.createElement("label");
    title.className = "title";
    title.htmlFor = box.id;
    title.textContent = task.title;

    const meta = document.createElement("div");
    meta.className = "meta";
    const parts = [`#${task.id}`, `${task.priority} priority`];
    meta.textContent = parts.join(", ");
    const due = formatDue(task.due_date);
    if (due) {
      meta.append(", ");
      const span = document.createElement("span");
      if (due.overdue && task.status !== "done") {
        span.className = "overdue";
        span.textContent = `overdue since ${due.label}`;
      } else {
        span.textContent = `due ${due.label}`;
      }
      meta.appendChild(span);
    }

    li.append(box, title, meta);
    els.taskList.appendChild(li);
  }
}

// ---------- SECTION 3: NETWORK ----------
async function send(url, body) {
  setBusy(true);
  const thinking = addMessage("Thinking…", "bot thinking");
  try {
    const data = await callApi("POST", url, body);
    thinking.remove();
    if (data.reply) addMessage(data.reply, "bot");
    if (data.confirm) addConfirm(data.confirm);
    renderTasks(data.tasks);
  } catch (err) {
    thinking.remove();
    addMessage(err.message || "Can't reach the server. Check that uvicorn is running.", "error");
  } finally {
    setBusy(false);
  }
}

async function loadTasks() {
  try {
    const res = await fetch(`${API}/tasks`);
    renderTasks(await res.json());
  } catch {
    els.tasksEmpty.hidden = false;
    els.tasksEmpty.textContent = "Can't load tasks. Check that the server is running.";
  }
}

async function toggleTask(id) {
  await fetch(`${API}/tasks/${id}/toggle`, { method: "POST" });
  loadTasks();
}

// Redraw the conversation after a page refresh
async function loadHistory() {
  try {
    const res = await fetch(`${API}/history/${threadId}`);
    const data = await res.json();
    for (const m of data.messages) addMessage(m.text, m.role);
    if (data.confirm) addConfirm(data.confirm);
  } catch {
    /* no history yet, nothing to show */
  }
}

function setBusy(busy) {
  els.send.disabled = busy;
  els.input.disabled = busy;
  // leave focus on the confirm buttons if a question is waiting
  const waiting = els.messages.querySelector(".confirm:not(.answered)");
  if (!busy && !waiting) els.input.focus();
}

// ---------- SECTION 4: EVENTS ----------
els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = els.input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  els.input.value = "";
  autoGrow();
  send(`${API}/chat`, { thread_id: threadId, message: text });
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
    els.input.value = chip.textContent.replace(/["]/g, '"');
    els.form.requestSubmit();
  })
);

els.newChat.addEventListener("click", () => {
  localStorage.removeItem("thread_id");
  threadId = getThreadId();
  els.messages.replaceChildren(els.empty);
  els.empty.hidden = false;
  els.inspector.hidden = true;
  els.input.focus();
});

loadHistory();
loadTasks();
