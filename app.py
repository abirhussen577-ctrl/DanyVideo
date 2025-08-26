from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Downloads folder
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Auto select cookie file based on URL
def get_cookiefile(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "cookies/youtube.txt"
    elif "facebook.com" in url:
        return "cookies/fb.txt"
    elif "instagram.com" in url:
        return "cookies/ig.txt"
    elif "tiktok.com" in url:
        return "cookies/tiktok.txt"
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    cookie_file = get_cookiefile(url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title).80s-%(id)s.%(ext)s"),
    }

    if cookie_file and os.path.exists(cookie_file):
        ydl_opts["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("filesize") and f.get("ext"):
                formats.append({
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("resolution") or f.get("format_note", ""),
                    "filesize": round(f["filesize"] / (1024 * 1024), 2) if f.get("filesize") else "?"
                })

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
