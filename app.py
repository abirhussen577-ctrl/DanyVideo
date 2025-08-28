from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        ydl_opts = {"quiet": True, "dump_single_json": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("url") and f.get("ext") in ["mp4", "webm"]:
                formats.append({
                    "quality": f.get("format_note", "N/A"),
                    "ext": f.get("ext"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url")
                })

        return render_template("result.html", title=info.get("title"), formats=formats)

    return render_template("index.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
