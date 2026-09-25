const API_BASE = window.API_BASE_URL || "";

const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const samplePromptsEl = document.getElementById("sample-prompts");

function renderMarkdown(text) {
  if (!window.marked) return text;
  const html = marked.parse(text, { breaks: true });
  const clean = window.DOMPurify ? DOMPurify.sanitize(html) : html;
  // wrap tables so wide markdown tables scroll horizontally on small screens
  return clean.replace(/<table>/g, '<div class="table-scroll"><table>').replace(/<\/table>/g, "</table></div>");
}

function clearEmptyState() {
  const empty = chatLog.querySelector(".empty-state");
  if (empty) empty.remove();
}

function addMessage(role, { text, html, pending } = {}) {
  clearEmptyState();
  const row = document.createElement("div");
  row.className = `chat-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "🙂" : "🍽️";

  const bubble = document.createElement("div");
  bubble.className = `chat-msg ${role}${pending ? " pending" : ""}`;
  if (html) bubble.innerHTML = html;
  else bubble.textContent = text;

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}

const THINKING_STAGES = [
  "Reading your message...",
  "Understanding your preferences...",
  "Searching the restaurant & recipe index...",
  "Weighing trends, styles, and nutrition...",
  "Putting together your recommendations...",
];

function startTypingIndicator() {
  const bubble = addMessage("bot", { pending: true, html: "" });
  bubble.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span><span class="status-text"></span>`;
  const statusEl = bubble.querySelector(".status-text");

  let i = 0;
  statusEl.textContent = THINKING_STAGES[0];
  const interval = setInterval(() => {
    i = (i + 1) % THINKING_STAGES.length;
    statusEl.textContent = THINKING_STAGES[i];
  }, 4000);

  return {
    bubble,
    stop() {
      clearInterval(interval);
    },
  };
}

async function sendMessage(message) {
  addMessage("user", { text: message });
  const typing = startTypingIndicator();
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `request failed (${res.status})`);
    typing.stop();
    typing.bubble.classList.remove("pending");
    typing.bubble.innerHTML = renderMarkdown(data.reply || "");
  } catch (err) {
    typing.stop();
    typing.bubble.classList.remove("pending");
    typing.bubble.classList.add("error");
    typing.bubble.textContent = `Something went wrong: ${err.message}`;
  } finally {
    sendBtn.disabled = false;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  autoResize();
  sendMessage(message);
});

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

function autoResize() {
  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 140)}px`;
}
chatInput.addEventListener("input", autoResize);

clearBtn.addEventListener("click", () => {
  chatLog.innerHTML = `<div class="empty-state"><span class="empty-emoji">👋</span><p>Tell me what you're craving, or tap a suggestion below to get started.</p></div>`;
});

async function loadSamplePrompts() {
  try {
    const res = await fetch(`${API_BASE}/api/sample-prompts`);
    const data = await res.json();
    samplePromptsEl.innerHTML = "";
    (data.prompts || []).forEach((prompt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = prompt;
      btn.addEventListener("click", () => {
        chatInput.value = prompt;
        autoResize();
        chatInput.focus();
      });
      samplePromptsEl.appendChild(btn);
    });
  } catch (err) {
    // sample prompts are a convenience, not critical - fail silently
  }
}

// ---------- Tabs ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.remove("active");
      b.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    if (btn.dataset.tab === "manage") loadRestaurants();
  });
});

// ---------- Manage Restaurants ----------
const restaurantList = document.getElementById("restaurant-list");

async function loadRestaurants() {
  restaurantList.innerHTML = "<li>Loading...</li>";
  try {
    const res = await fetch(`${API_BASE}/api/restaurants`);
    const records = await res.json();
    if (!records.length) {
      restaurantList.innerHTML = "<li>(no restaurants yet)</li>";
      return;
    }
    restaurantList.innerHTML = "";
    records.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `${r.id}: ${r.name} (${r.cuisine}, ${r.location}) - ${r.price_range} - ${r.rating}`;
      restaurantList.appendChild(li);
    });
  } catch (err) {
    restaurantList.innerHTML = `<li>Could not load restaurants: ${err.message}</li>`;
  }
}

document.getElementById("refresh-restaurants").addEventListener("click", loadRestaurants);

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const raw_text = document.getElementById("add-raw-text").value.trim();
  const resultEl = document.getElementById("add-result");
  if (!raw_text) return;
  resultEl.textContent = "Adding...";
  try {
    const res = await fetch(`${API_BASE}/api/restaurants`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "could not add restaurant");
    resultEl.textContent = `Added: ${data.name} (id=${data.id})`;
    document.getElementById("add-raw-text").value = "";
    loadRestaurants();
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
  }
});

document.getElementById("update-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("update-id").value.trim();
  const rating = parseFloat(document.getElementById("update-rating").value);
  const resultEl = document.getElementById("update-result");
  if (!id || Number.isNaN(rating)) return;
  resultEl.textContent = "Updating...";
  try {
    const res = await fetch(`${API_BASE}/api/restaurants/${encodeURIComponent(id)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updates: { rating } }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "could not update restaurant");
    resultEl.textContent = `Updated ${id} rating to ${rating}.`;
    loadRestaurants();
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
  }
});

document.getElementById("delete-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("delete-id").value.trim();
  const resultEl = document.getElementById("delete-result");
  if (!id) return;
  resultEl.textContent = "Deleting...";
  try {
    const res = await fetch(`${API_BASE}/api/restaurants/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok && res.status !== 204) {
      const data = await res.json();
      throw new Error(data.detail || "could not delete restaurant");
    }
    resultEl.textContent = `Deleted ${id}.`;
    loadRestaurants();
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
  }
});

loadSamplePrompts();
