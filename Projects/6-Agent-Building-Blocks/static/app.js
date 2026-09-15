// ---------- SECTION 1: SHARED "API INSPECTOR" HELPER ----------
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

function renderTrace(container, steps, describe) {
  container.innerHTML = "";
  steps.forEach((step) => {
    const div = document.createElement("div");
    div.className = "trace-step" + (step.role === "tool" ? " tool-result" : "");
    div.innerHTML = describe(step);
    container.appendChild(div);
  });
}

// ---------- SECTION 2: TOOL CREATION & INSPECTION ----------
let toolSchemas = [];

async function loadTools() {
  const data = await callApi("GET", "/api/tools");
  toolSchemas = data.tools;

  const list = document.getElementById("tool-list");
  list.innerHTML = "";
  const select = document.getElementById("tool-select");
  select.innerHTML = "";

  toolSchemas.forEach((t) => {
    const row = document.createElement("div");
    row.className = "tool-row";
    row.innerHTML =
      `<span class="tool-name">${t.name}</span>` +
      `<span class="tool-desc">${t.description}</span>` +
      `<span class="badge">${t.creation_method}</span>`;
    list.appendChild(row);

    const opt = document.createElement("option");
    opt.value = t.name;
    opt.textContent = `${t.name}(${Object.keys(t.args).join(", ")})`;
    select.appendChild(opt);
  });

  updateToolInputPlaceholder();
}
loadTools();

function updateToolInputPlaceholder() {
  const name = document.getElementById("tool-select").value;
  const schema = toolSchemas.find((t) => t.name === name);
  if (!schema) return;
  const argNames = Object.keys(schema.args);
  document.getElementById("tool-input").placeholder =
    argNames.length <= 1 ? `Value for "${argNames[0]}"` : `${argNames.join(", ")} (comma-separated)`;
}
document.getElementById("tool-select").addEventListener("change", updateToolInputPlaceholder);

document.getElementById("tool-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("tool-select").value;
  const rawInput = document.getElementById("tool-input").value;
  const schema = toolSchemas.find((t) => t.name === name);
  const argNames = Object.keys(schema.args);

  // Single-arg tools take the raw string; multi-arg tools expect "a, b" CSV.
  let input;
  if (argNames.length <= 1) {
    const key = argNames[0] || "text";
    const val = isNaN(rawInput) ? rawInput : Number(rawInput);
    input = { [key]: val };
  } else {
    const parts = rawInput.split(",").map((p) => p.trim());
    input = {};
    argNames.forEach((key, i) => {
      const val = parts[i] ?? "";
      input[key] = isNaN(val) ? val : Number(val);
    });
  }

  const data = await callApi(
    "POST",
    "/api/tools/invoke",
    { name, input },
    document.getElementById("tool-inspector")
  );
  document.getElementById("tool-output").textContent = JSON.stringify(data.output);
  document.getElementById("tool-result").hidden = false;
});

// ---------- SECTION 3: MANUAL TOOL CALLING ----------
const manualForm = document.getElementById("manual-form");

async function runManualCalling(question) {
  const button = manualForm.querySelector("button");
  button.disabled = true;
  try {
    const data = await callApi(
      "POST",
      "/api/manual-calling",
      { question },
      document.getElementById("manual-inspector")
    );
    const container = document.getElementById("manual-trace");
    container.innerHTML = "";
    data.rounds.forEach((round, i) => {
      round.forEach((call) => {
        const div = document.createElement("div");
        div.className = "trace-step";
        div.innerHTML =
          `<span class="trace-label">Round ${i + 1} — tool call</span>` +
          `<code>${call.tool}(${JSON.stringify(call.args)})</code> → ${call.result}`;
        container.appendChild(div);
      });
    });
    if (data.final_answer) {
      const div = document.createElement("div");
      div.className = "trace-step tool-result";
      div.innerHTML = `<span class="trace-label">Final answer</span>${data.final_answer}`;
      container.appendChild(div);
    }
  } finally {
    button.disabled = false;
  }
}

manualForm.addEventListener("submit", (e) => {
  e.preventDefault();
  runManualCalling(document.getElementById("manual-question").value);
});

document.querySelectorAll("#manual-examples .example-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById("manual-question").value = btn.dataset.question;
    runManualCalling(btn.dataset.question);
  });
});

// ---------- SECTION 4: LCEL RUNNABLES ----------
document.getElementById("lcel-parallel-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = document.getElementById("lcel-parallel-text").value;
  const data = await callApi("POST", "/api/lcel/parallel", { text }, document.getElementById("lcel-inspector"));
  document.getElementById("lcel-parallel-summary").textContent = data.summary;
  document.getElementById("lcel-parallel-translation").textContent = data.translation;
  document.getElementById("lcel-parallel-result").hidden = false;
});

document.getElementById("lcel-passthrough-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = document.getElementById("lcel-passthrough-text").value;
  const data = await callApi("POST", "/api/lcel/passthrough", { question }, document.getElementById("lcel-inspector"));
  document.getElementById("lcel-passthrough-question").textContent = data.question;
  document.getElementById("lcel-passthrough-answer").textContent = data.answer;
  document.getElementById("lcel-passthrough-result").hidden = false;
});

document.getElementById("lcel-lambda-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = document.getElementById("lcel-lambda-text").value;
  const data = await callApi("POST", "/api/lcel/lambda", { text }, document.getElementById("lcel-inspector"));
  document.getElementById("lcel-lambda-count").textContent = data.word_count;
  document.getElementById("lcel-lambda-result").hidden = false;
});

document.getElementById("lcel-branch-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = document.getElementById("lcel-branch-text").value;
  const data = await callApi("POST", "/api/lcel/branch", { text }, document.getElementById("lcel-inspector"));
  document.getElementById("lcel-branch-taken").textContent = data.branch_taken;
  document.getElementById("lcel-branch-reply").textContent = data.reply;
  document.getElementById("lcel-branch-result").hidden = false;
});

// ---------- SECTION 5: ORCHESTRATING AGENT (traced) ----------
document.getElementById("support-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = document.getElementById("support-question").value;
  const data = await callApi(
    "POST",
    "/api/support/traced",
    { question },
    document.getElementById("support-inspector")
  );
  renderTrace(document.getElementById("support-trace"), data.steps, (step) => {
    if (step.tool_calls) {
      return `<span class="trace-label">Agent requests a tool</span>` +
        step.tool_calls.map((c) => `<code>${c.tool}(${JSON.stringify(c.args)})</code>`).join(", ");
    }
    if (step.role === "tool") {
      return `<span class="trace-label">Tool result — ${step.name}</span>${step.result}`;
    }
    return `<span class="trace-label">Final answer</span>${step.final_answer}`;
  });
});

// ---------- SECTION 6: AGENT MEMORY (multi-turn chat) ----------
let supportSessionId = null;

async function ensureSupportSession() {
  if (supportSessionId) return supportSessionId;
  const data = await callApi("GET", "/api/new-session");
  supportSessionId = data.session_id;
  return supportSessionId;
}

function appendChatMsg(windowId, role, text) {
  const win = document.getElementById(windowId);
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

document.getElementById("support-chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("support-chat-input");
  const message = input.value;
  input.value = "";
  appendChatMsg("support-chat-window", "user", message);

  await ensureSupportSession();
  const data = await callApi(
    "POST",
    "/api/support/chat",
    { session_id: supportSessionId, message },
    document.getElementById("support-chat-inspector")
  );
  appendChatMsg("support-chat-window", "ai", data.reply);
});

// ---------- SECTION 7: SQL AGENT ----------
const sqlForm = document.getElementById("sql-form");

async function askSqlAgent(question) {
  const button = sqlForm.querySelector("button");
  button.disabled = true;
  try {
    const data = await callApi(
      "POST",
      "/api/sql-agent",
      { question },
      document.getElementById("sql-inspector")
    );
    document.getElementById("sql-answer").textContent = data.answer;
    document.getElementById("sql-result").hidden = false;
    renderTrace(document.getElementById("sql-trace"), data.steps, (step) => {
      return `<span class="trace-label">${step.tool}</span>` +
        `<code>${JSON.stringify(step.tool_input)}</code> → ${step.observation}`;
    });
  } finally {
    button.disabled = false;
  }
}

sqlForm.addEventListener("submit", (e) => {
  e.preventDefault();
  askSqlAgent(document.getElementById("sql-question").value);
});

document.querySelectorAll('.example-btn[data-target="sql-question"]').forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById("sql-question").value = btn.dataset.question;
    askSqlAgent(btn.dataset.question);
  });
});

// ---------- SECTION 8: DATA-VISUALIZATION AGENT ----------
document.getElementById("viz-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = document.getElementById("viz-request").value;
  const data = await callApi("POST", "/api/viz-agent", { text }, document.getElementById("viz-inspector"));

  document.getElementById("viz-reply").textContent = data.reply;
  document.getElementById("viz-result").hidden = false;

  const img = document.getElementById("viz-chart");
  if (data.chart_base64) {
    img.src = `data:image/png;base64,${data.chart_base64}`;
    img.hidden = false;
  } else {
    img.hidden = true;
  }

  renderTrace(document.getElementById("viz-trace"), data.steps, (step) => {
    if (step.tool_calls) {
      return `<span class="trace-label">Agent requests a tool</span>` +
        step.tool_calls.map((c) => `<code>${c.tool}(${JSON.stringify(c.args)})</code>`).join(", ");
    }
    return `<span class="trace-label">Tool result — ${step.name}</span>${step.result}`;
  });
});
