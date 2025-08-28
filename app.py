from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# cookies path define
COOKIES = {
    "youtube.com": "cookies/youtube.txt",
    "youtu.be": "cookies/youtube.txt",
    "facebook.com": "cookies/fb.txt",
    "fb.watch": "cookies/fb.txt",
    "instagram.com": "cookies/ig.txt",
    "tiktok.com": "cookies/tiktok.txt",
}


def get_cookie_file(url):
    for domain, path in COOKIES.items():
        if domain in url:
            if os.path.exists(path):
                return path
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "❌ No URL provided"}), 400

    cookie_file = get_cookie_file(url)

    ydl_opts = {
        "quiet": True,
        "format": "best",
        "noplaylist": True,
    }

    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("resolution") or f.get("height"),
                    "filesize": f.get("filesize"),
                    "url": f["url"],
                }
                for f in info.get("formats", [])
                if f.get("url")
            ]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
