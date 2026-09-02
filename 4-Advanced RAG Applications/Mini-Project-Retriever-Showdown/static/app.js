// ---------- SECTION 1: SHARED "API INSPECTOR" HELPER ----------
async function callApi(method, url, body, inspectorPreEl) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json();

  if (inspectorPreEl) {
    inspectorPreEl.textContent =
      `${method} ${url}\n\nRequest body:\n${JSON.stringify(body, null, 2)}\n\n` +
      `Response (${res.status}):\n${JSON.stringify(data, null, 2)}`;
  }
  return data;
}

function renderChunkList(listEl, texts) {
  listEl.innerHTML = "";
  texts.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    listEl.appendChild(li);
  });
}

function renderScoredList(listEl, items) {
  listEl.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `${item.text} <span class="score">(score: ${item.score.toFixed(4)})</span>`;
    listEl.appendChild(li);
  });
}

// ---------- SECTION 2: LOAD THE CORPUS ONCE ON PAGE LOAD ----------
async function loadCorpus() {
  const data = await callApi("GET", "/api/corpus");
  const listEl = document.getElementById("corpus-list");
  listEl.innerHTML = "";
  data.documents.forEach((doc) => {
    const li = document.createElement("li");
    li.textContent = doc;
    listEl.appendChild(li);
  });
}
loadCorpus();

// ---------- SECTION 3: RUN ALL FIVE RETRIEVERS ON SUBMIT ----------
const form = document.getElementById("query-form");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const question = document.getElementById("question").value;
    const body = { question };

    const [baseline, mmr, multiquery, bm25, rrf] = await Promise.all([
      callApi("POST", "/api/baseline", body, document.getElementById("baseline-inspector")),
      callApi("POST", "/api/mmr", body, document.getElementById("mmr-inspector")),
      callApi("POST", "/api/multiquery", body, document.getElementById("multiquery-inspector")),
      callApi("POST", "/api/bm25", body, document.getElementById("bm25-inspector")),
      callApi("POST", "/api/rrf", body, document.getElementById("rrf-inspector")),
    ]);

    renderChunkList(document.getElementById("baseline-results"), baseline.results);
    renderChunkList(document.getElementById("mmr-results"), mmr.results);

    renderChunkList(document.getElementById("multiquery-generated"), multiquery.generated_queries);
    renderChunkList(document.getElementById("multiquery-results"), multiquery.merged_results);

    renderChunkList(document.getElementById("bm25-results"), bm25.results);
    renderScoredList(document.getElementById("rrf-results"), rrf.results);

    document.getElementById("results-grid").hidden = false;
  } catch (err) {
    alert(err.message);
  } finally {
    button.disabled = false;
  }
});
