from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/getinfo", methods=["POST"])
def getinfo():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = [
            {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "format_note": f.get("format_note"),
                "resolution": f.get("resolution")
            }
            for f in info.get("formats", [])
            if f.get("ext") in ["mp4", "webm"]
        ]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download")
def download():
    url = request.args.get("url")
    format_id = request.args.get("format_id")

    if not url or not format_id:
        return "❌ Invalid request", 400

    try:
        ydl_opts = {
            "format": format_id,
            "outtmpl": "downloads/%(title)s.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
