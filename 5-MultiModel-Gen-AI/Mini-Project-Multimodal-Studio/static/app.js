// ---------- SECTION 1: HELPERS ----------
function showInspector(id, request, response) {
  const el = document.getElementById(id);
  el.hidden = false;
  el.querySelector("pre").textContent =
    "REQUEST:\n" + JSON.stringify(request, null, 2) + "\n\nRESPONSE:\n" + JSON.stringify(response, null, 2);
}

// Groq errors (missing model access, terms not accepted, etc.) come back as
// {"detail": "..."} with a non-2xx status — show that instead of failing silently.
async function showErrorIfAny(res, resultId, textId) {
  if (res.ok) return false;
  let detail = `Request failed (HTTP ${res.status}).`;
  try {
    detail = (await res.json()).detail || detail;
  } catch {
    /* body wasn't JSON, fall back to the generic message above */
  }
  document.getElementById(resultId).hidden = false;
  document.getElementById(textId).textContent = "⚠ " + detail;
  return true;
}

// ---------- SECTION 2: IMAGE CAPTIONING / VQA ----------
const captionInput = document.getElementById("caption-image");
captionInput.addEventListener("change", () => {
  const file = captionInput.files[0];
  if (!file) return;
  const preview = document.getElementById("caption-preview");
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

document.getElementById("caption-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = captionInput.files[0];
  const question = document.getElementById("caption-question").value;
  const form = new FormData();
  form.append("image", file);
  form.append("question", question);

  const res = await fetch("/api/caption", { method: "POST", body: form });
  if (await showErrorIfAny(res, "caption-result", "caption-text")) return;
  const data = await res.json();

  document.getElementById("caption-result").hidden = false;
  document.getElementById("caption-text").textContent = data.result;
  showInspector("caption-inspector", { image: file.name, question }, data);
});

// ---------- SECTION 3: SPEECH-TO-TEXT (upload or record) ----------
let mediaRecorder = null;
let recordedChunks = [];

document.getElementById("record-btn").addEventListener("click", async () => {
  const btn = document.getElementById("record-btn");
  const status = document.getElementById("record-status");

  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  recordedChunks = [];

  mediaRecorder.ondataavailable = (e) => recordedChunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    const file = new File([blob], "recording.webm", { type: "audio/webm" });
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById("transcribe-file").files = dt.files;
    btn.classList.remove("recording");
    status.textContent = "Recorded — press Transcribe.";
    stream.getTracks().forEach((t) => t.stop());
  };

  mediaRecorder.start();
  btn.classList.add("recording");
  status.textContent = "Recording... click Record again to stop.";
});

document.getElementById("transcribe-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = document.getElementById("transcribe-file").files[0];
  if (!file) {
    document.getElementById("record-status").textContent = "Upload a file or record audio first.";
    return;
  }
  const form = new FormData();
  form.append("audio", file);

  const res = await fetch("/api/transcribe", { method: "POST", body: form });
  if (await showErrorIfAny(res, "transcribe-result", "transcribe-text")) return;
  const data = await res.json();

  document.getElementById("transcribe-result").hidden = false;
  document.getElementById("transcribe-text").textContent = data.transcript;
  showInspector("transcribe-inspector", { audio: file.name }, data);
});

// ---------- SECTION 4: TEXT-TO-SPEECH ----------
document.getElementById("speak-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = document.getElementById("speak-text").value;
  const res = await fetch("/api/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (await showErrorIfAny(res, "speak-result", "speak-error")) return;
  const blob = await res.blob();
  const audio = document.getElementById("speak-audio");
  audio.src = URL.createObjectURL(blob);
  audio.hidden = false;
  audio.play();
});

// ---------- SECTION 5: FUSION — PICTURE TO NARRATION ----------
document.getElementById("narrate-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = document.getElementById("narrate-image").files[0];
  const form = new FormData();
  form.append("image", file);

  const res = await fetch("/api/narrate", { method: "POST", body: form });
  if (await showErrorIfAny(res, "narrate-result", "narrate-caption")) return;
  const data = await res.json();

  document.getElementById("narrate-result").hidden = false;
  document.getElementById("narrate-caption").textContent = data.caption;

  const audio = document.getElementById("narrate-audio");
  audio.src = "data:audio/wav;base64," + data.audio_base64;
  audio.hidden = false;
  audio.play();
});
