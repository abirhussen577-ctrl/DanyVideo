const mount = document.getElementById("resultMount");
const form = document.getElementById("urlForm");
const input = document.getElementById("urlInput");
const btn = document.getElementById("getBtn");

function show(html) {
  mount.innerHTML = html;
  mount.classList.remove("hidden");
  mount.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showError(msg) {
  const safe = (msg || "Unknown error").toString().slice(0, 800);
  show(`<div class="card error-card shake-in">
         <h3>Oops! Something went wrong.</h3>
         <p>${safe}</p>
       </div>`);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = (input.value || "").trim();
  if (!url) { showError("Please enter a URL."); return; }

  btn.disabled = true; btn.textContent = "Loading...";

  try {
    const res = await fetch("/api/inspect", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ url })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }

    // Build result HTML from result.html-like structure
    const title = data.title;
    const thumb = data.thumbnail || "";
    const entries = data.entries || [];

    const links = entries.map(it => {
      const q = new URLSearchParams({ url, format_id: it.format_id, ext: it.ext });
      return `<a class="format-btn" href="/download?${q.toString()}" download>
                ${it.label} ${it.kind === "audio" ? '<span class="tag">audio</span>' : ''}
              </a>`;
    }).join("");

    const html = `
      <div class="card result-card fade-in">
        <div class="media">
          ${thumb ? `<img class="thumb" src="${thumb}" alt="thumbnail">` : ""}
          <div class="meta"><h3 class="title">${title}</h3></div>
        </div>
        <div class="formats">${links}</div>
      </div>
    `;
    show(html);
  } catch (err) {
    showError(err.message || err);
  } finally {
    btn.disabled = false; btn.textContent = "Get Video";
  }
});
