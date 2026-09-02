// ---------- SECTION 1: HELPERS ----------
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function showInspector(id, request, response) {
  const el = document.getElementById(id);
  el.hidden = false;
  el.querySelector("pre").textContent =
    "REQUEST:\n" + JSON.stringify(request, null, 2) + "\n\nRESPONSE:\n" + JSON.stringify(response, null, 2);
}

function renderMatches(container, matches) {
  container.hidden = false;
  container.innerHTML = "";
  if (matches.length === 0) {
    container.innerHTML = '<div class="stage"><p>No matches for these filters.</p></div>';
    return;
  }
  matches.forEach((m) => {
    const div = document.createElement("div");
    div.className = "stage match";
    div.innerHTML = `<span class="stage-label">${m.metadata.topic} · ${m.metadata.source} · ${m.metadata.year}
      <span class="dist">dist=${m.distance.toFixed(4)}</span></span><p>${m.document}</p>`;
    container.appendChild(div);
  });
}

// ---------- SECTION 2: COLLECTION INFO ----------
async function loadInfo() {
  const info = await (await fetch("/api/collection-info")).json();
  document.getElementById("info-count").textContent = info.count;
  document.getElementById("info-topics").textContent = info.topics.join(", ");
  document.getElementById("info-sources").textContent = info.sources.join(", ");
  document.getElementById("info-hnsw").textContent =
    `space=${info.hnsw.space}, ef_construction=${info.hnsw.ef_construction}, max_neighbors=${info.hnsw.max_neighbors}`;

  const topicSel = document.getElementById("filter-topic");
  info.topics.forEach((t) => topicSel.add(new Option(t, t)));
  const sourceSel = document.getElementById("filter-source");
  info.sources.forEach((s) => sourceSel.add(new Option(s, s)));
}

// ---------- SECTION 3: PURE VECTOR SEARCH ----------
document.getElementById("search-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    query: document.getElementById("search-query").value,
    top_k: Number(document.getElementById("search-topk").value),
  };
  const data = await postJSON("/api/search", body);
  renderMatches(document.getElementById("search-result"), data.matches);
  showInspector("search-inspector", body, data);
});

// ---------- SECTION 4: FILTERED SEARCH ----------
document.getElementById("filter-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    query: document.getElementById("filter-query").value,
    top_k: 3,
    topic: document.getElementById("filter-topic").value || null,
    source: document.getElementById("filter-source").value || null,
    contains: document.getElementById("filter-contains").value || null,
  };
  const data = await postJSON("/api/search", body);
  renderMatches(document.getElementById("filter-result"), data.matches);
  showInspector("filter-inspector", body, data);
});

// ---------- SECTION 5: HNSW TUNING ----------
document.getElementById("ef-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = { ef_search: Number(document.getElementById("ef-value").value) };
  const data = await postJSON("/api/tune-ef", body);
  document.getElementById("ef-result").hidden = false;
  document.getElementById("ef-applied").textContent =
    `ef_search is now ${data.ef_search} — every search above uses this from now on.`;
});

// ---------- SECTION 6: RAG ASK ----------
document.getElementById("ask-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = { question: document.getElementById("ask-question").value, top_k: 3 };
  const data = await postJSON("/api/ask", body);
  document.getElementById("ask-result").hidden = false;
  document.getElementById("ask-answer").textContent = data.answer;
  showInspector("ask-inspector", body, data.retrieved);
});

loadInfo();
