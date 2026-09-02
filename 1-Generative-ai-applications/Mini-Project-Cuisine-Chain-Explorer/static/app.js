// ---------- SECTION 1: SHARED "API INSPECTOR" HELPER ----------
// Every demo below calls this so the raw request/response is visible on screen,
// not just the parsed result -- that visibility is the point of this frontend.
async function callApi(method, url, body, inspectorEl) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json();

  if (inspectorEl) {
    const pre = inspectorEl.querySelector("pre");
    pre.textContent =
      `${method} ${url}\n\n` +
      `Request body:\n${body ? JSON.stringify(body, null, 2) : "(none)"}\n\n` +
      `Response (${res.status}):\n${JSON.stringify(data, null, 2)}`;
    inspectorEl.hidden = false;
  }
  return data;
}

// ---------- SECTION 2: SEQUENTIAL CHAIN PANEL ----------
const seqForm = document.getElementById("sequential-form");
seqForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = seqForm.querySelector("button");
  button.disabled = true;
  try {
    const location = document.getElementById("location").value;
    const data = await callApi(
      "POST",
      "/api/sequential",
      { location },
      document.getElementById("sequential-inspector")
    );
    document.getElementById("seq-dish").textContent = data.dish;
    document.getElementById("seq-recipe").textContent = data.recipe;
    document.getElementById("seq-time").textContent = data.time;
    document.getElementById("sequential-result").hidden = false;
  } finally {
    button.disabled = false;
  }
});

// ---------- SECTION 3: PARALLEL CHAIN PANEL ----------
const parForm = document.getElementById("parallel-form");
parForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = parForm.querySelector("button");
  button.disabled = true;
  try {
    const dish = document.getElementById("dish").value;
    const data = await callApi(
      "POST",
      "/api/parallel",
      { dish },
      document.getElementById("parallel-inspector")
    );
    document.getElementById("par-fact").textContent = data.fact;
    document.getElementById("par-joke").textContent = data.joke;
    document.getElementById("parallel-result").hidden = false;
  } finally {
    button.disabled = false;
  }
});

// ---------- SECTION 4: BRANCH CHAIN PANEL ----------
const branchForm = document.getElementById("branch-form");
branchForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = branchForm.querySelector("button");
  button.disabled = true;
  try {
    const topic = document.getElementById("topic").value;
    const detailed = document.getElementById("detailed").checked;
    const data = await callApi(
      "POST",
      "/api/branch",
      { topic, detailed },
      document.getElementById("branch-inspector")
    );
    document.getElementById("branch-explanation").textContent = data.explanation;
    document.getElementById("branch-result").hidden = false;
  } finally {
    button.disabled = false;
  }
});

// ---------- SECTION 5: CONVERSATIONAL MEMORY PANEL ----------
let sessionId = null;

async function ensureSession() {
  if (sessionId) return sessionId;
  const data = await callApi("GET", "/api/new-session");
  sessionId = data.session_id;
  return sessionId;
}

function appendChatMsg(role, text) {
  const win = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

const chatForm = document.getElementById("chat-form");
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value;
  input.value = "";
  appendChatMsg("user", message);

  await ensureSession();
  const data = await callApi(
    "POST",
    "/api/chat",
    { session_id: sessionId, message },
    document.getElementById("chat-inspector")
  );
  appendChatMsg("ai", data.reply);
});
