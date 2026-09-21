// Plain JS, no build step. Talks to the FastAPI backend on the same origin.

function setBusy(form, busy) {
  form.querySelector("button").disabled = busy;
}

async function post(endpoint, body) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

// ---------- SECTION 1: CREWAI ----------
async function runCrewai(form) {
  const topic = form.topic.value.trim();
  const result = document.getElementById("crewai-result");
  const research = document.getElementById("crewai-research");
  const pitch = document.getElementById("crewai-pitch");
  setBusy(form, true);
  research.textContent = "Running the crew (researcher, then writer)…";
  pitch.textContent = "";
  research.classList.remove("error");
  result.hidden = false;
  try {
    const data = await post("/api/crewai", { topic });
    research.textContent = data.research;
    pitch.textContent = data.pitch;
  } catch (err) {
    research.classList.add("error");
    research.textContent = err.message;
  } finally {
    setBusy(form, false);
  }
}

// ---------- SECTION 2: AUTOGEN ----------
async function runAutogen(form) {
  const topic = form.topic.value.trim();
  const result = document.getElementById("autogen-result");
  const transcript = document.getElementById("autogen-transcript");
  const stop = document.getElementById("autogen-stop");
  setBusy(form, true);
  transcript.replaceChildren(turnItem("system", "Running the round-robin chat…"));
  stop.textContent = "";
  result.hidden = false;
  try {
    const data = await post("/api/autogen", { topic });
    transcript.replaceChildren(...data.turns.map((t) => turnItem(t.agent, t.text)));
    stop.textContent = `Stopped: ${data.stop_reason}`;
  } catch (err) {
    transcript.replaceChildren(turnItem("error", err.message));
  } finally {
    setBusy(form, false);
  }
}

function turnItem(agent, text) {
  const li = document.createElement("li");
  li.className = agent;
  const who = document.createElement("span");
  who.className = "who";
  who.textContent = agent;
  const body = document.createElement("span");
  body.textContent = text;
  li.append(who, body);
  return li;
}

// ---------- SECTION 3: BEEAI ----------
async function runBeeai(form) {
  const question = form.question.value.trim();
  const result = document.getElementById("beeai-result");
  const answer = document.getElementById("beeai-answer");
  const inspector = document.getElementById("beeai-inspector");
  setBusy(form, true);
  answer.textContent = "Running the ReAct loop…";
  answer.classList.remove("error");
  result.hidden = false;
  try {
    const data = await post("/api/beeai", { question });
    answer.textContent = data.answer;
    const pre = inspector.querySelector("pre");
    pre.textContent = data.tool_calls.length
      ? data.tool_calls
          .map((c) => `convert_currency(amount=${c.amount}, rate=${c.rate}) -> "${c.result}"`)
          .join("\n")
      : `Tool "${data.tool.name}" was available but never called — the agent answered without it.`;
  } catch (err) {
    answer.classList.add("error");
    answer.textContent = err.message;
  } finally {
    setBusy(form, false);
  }
}

// ---------- SECTION 4: WIRING ----------
const runners = { "/api/crewai": runCrewai, "/api/autogen": runAutogen, "/api/beeai": runBeeai };

document.querySelectorAll(".run-form").forEach((form) => {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    runners[form.dataset.endpoint](form);
  });
});

document.querySelectorAll(".chip[data-fill]").forEach((chip) => {
  chip.addEventListener("click", () => {
    const form = document.querySelector(`.run-form[data-endpoint="/api/${chip.dataset.fill}"]`);
    form.question.value = chip.textContent;
    form.requestSubmit();
  });
});
