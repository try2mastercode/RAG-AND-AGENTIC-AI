const API_BASE = window.API_BASE_URL || "";

const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const samplePromptsEl = document.getElementById("sample-prompts");

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `chat-msg ${role}`;
  el.textContent = text;
  chatLog.appendChild(el);
  chatLog.scrollTop = chatLog.scrollHeight;
  return el;
}

async function sendMessage(message) {
  addMessage("user", message);
  const pending = addMessage("bot pending", "Thinking...");
  sendBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error(`request failed (${res.status})`);
    const data = await res.json();
    pending.textContent = data.reply;
    pending.classList.remove("pending");
  } catch (err) {
    pending.textContent = `Something went wrong: ${err.message}`;
    pending.classList.remove("pending");
  } finally {
    sendBtn.disabled = false;
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  sendMessage(message);
});

clearBtn.addEventListener("click", () => {
  chatLog.innerHTML = "";
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
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
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
