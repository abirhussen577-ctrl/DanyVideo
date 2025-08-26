from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Download route
@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "No URL provided"})

        # yt-dlp options
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
            "cookiesfrombrowser": ("chrome",) if os.name == "nt" else None,
        }

        result_data = {}
        formats_list = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            result_data["title"] = info.get("title", "Untitled")
            result_data["thumbnail"] = info.get("thumbnail", "")

            # formats sorted by resolution (high → low)
            for f in info.get("formats", []):
                if f.get("url") and f.get("ext") in ["mp4", "m4a", "webm"]:
                    quality = f.get("format_note") or f.get("resolution") or f.get("ext")
                    formats_list.append({
                        "quality": f"{quality} ({f['ext']})",
                        "url": f["url"]
                    })

        # sort high → low
        formats_list = sorted(formats_list, key=lambda x: x["quality"], reverse=True)

        result_data["formats"] = formats_list

        return jsonify(result_data)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
