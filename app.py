from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": "best",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("filesize"):
                formats.append({
                    "format_id": f.get("format_id"),
                    "resolution": f.get("format_note") or f.get("height"),
                    "ext": f.get("ext"),
                    "filesize": round(f.get("filesize") / (1024*1024), 2)  # MB
                })

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "url": url,
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download_file', methods=['POST'])
def download_file():
    url = request.form.get('url')
    format_id = request.form.get('format_id')

    if not url or not format_id:
        return jsonify({"error": "Missing parameters"}), 400

    outtmpl = os.path.join(DOWNLOAD_FOLDER, "%(title).80s.%(ext)s")
    ydl_opts = {
        "format": format_id,
        "outtmpl": outtmpl,
        "merge_output_format": "mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)