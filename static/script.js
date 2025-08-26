document.getElementById("urlForm").onsubmit = async (e) => {
  e.preventDefault();

  let url = document.getElementById("url").value.trim();
  if (!url) {
    showNotification("Please enter a valid URL!", "error");
    return;
  }

  document.getElementById("result").innerHTML = `<p>⏳ Fetching video details...</p>`;

  try {
    let response = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: "url=" + encodeURIComponent(url),
    });

    let data = await response.json();

    if (data.error) throw new Error(data.error);

    let html = `
      <div class="video-card">
        <img src="${data.thumbnail}" alt="Thumbnail" class="thumbnail">
        <h3>${data.title}</h3>
        <p>Available Formats:</p>
        <div class="formats">
    `;

    data.formats.forEach((f) => {
      html += `
        <button class="format-btn" onclick="downloadVideo('${data.url}', '${f.format_id}')">
          ${f.resolution || "Unknown"} (${f.ext.toUpperCase()}) - ${f.filesize} MB
        </button>
      `;
    });

    html += `</div></div>`;
    document.getElementById("result").innerHTML = html;

  } catch (err) {
    document.getElementById("result").innerHTML = `<p style="color:red;">❌ Error: ${err.message}</p>`;
  }
};

async function downloadVideo(videoUrl, formatId) {
  showNotification("⬇️ Download started...", "success");

  let formData = new URLSearchParams();
  formData.append("url", videoUrl);
  formData.append("format_id", formatId);

  let response = await fetch("/download_file", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    showNotification("❌ Download failed!", "error");
    return;
  }

  let blob = await response.blob();
  let link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "video.mp4";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function showNotification(message, type) {
  let notif = document.createElement("div");
  notif.className = "notification " + type;
  notif.innerText = message;
  document.body.appendChild(notif);

  setTimeout(() => {
    notif.remove();
  }, 3000);
}
