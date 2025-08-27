document.getElementById("urlForm").onsubmit = async (e) => {
  e.preventDefault();
  const url = document.getElementById("url").value.trim();
  if (!url) {
    showNotification("Please enter a valid URL!", "error");
    return;
  }

  document.getElementById("resultBox").innerHTML = `<p>⏳ Fetching video details...</p>`;

  try {
    const response = await fetch("/get_info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    document.getElementById("resultBox").style.display = "block";
    document.getElementById("thumbnail").src = data.thumbnail;
    document.getElementById("title").textContent = data.title;

    const formatsList = document.getElementById("formatsList");
    formatsList.innerHTML = "";

    data.formats.forEach((f) => {
      const row = `
        <tr>
          <td>${f.resolution}</td>
          <td>${f.ext.toUpperCase()}</td>
          <td>${f.filesize_mb || "Unknown"}</td>
          <td><button class="format-btn" onclick="downloadVideo('${url}', '${f.format_id}', '${data.title}', '${f.ext}')">⬇️ Download</button></td>
        </tr>
      `;
      formatsList.innerHTML += row;
    });
  } catch (err) {
    showNotification(`❌ Error: ${err.message}`, "error");
  }
};

async function downloadVideo(url, formatId, title, ext) {
  showNotification("⬇️ Download started...", "success");

  try {
    const formData = new URLSearchParams();
    formData.append("url", url);
    formData.append("format_id", formatId);

    const response = await fetch("/download_file", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Download failed");

    const blob = await response.blob();
    const filename = `${title.replace(/[\/\\]/g, '_')}.${ext}`;
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    showNotification(`❌ Error: ${err.message}`, "error");
  }
}

function showNotification(message, type) {
  const notif = document.getElementById("notify");
  notif.textContent = message;
  notif.className = `notification ${type}`;
  notif.style.display = "block";
  setTimeout(() => {
    notif.style.display = "none";
  }, 3000);
}
