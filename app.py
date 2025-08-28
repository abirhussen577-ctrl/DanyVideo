from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")

        if not url:
            return render_template("result.html", title="No URL provided", formats=[])

        try:
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "Unknown title")

                formats = []
                for f in info.get("formats", []):
                    if f.get("url") and f.get("ext"):
                        formats.append({
                            "quality": f.get("format_note", "N/A"),
                            "ext": f.get("ext"),
                            "filesize": f.get("filesize"),
                            "url": f.get("url"),
                        })

            return render_template("result.html", title=title, formats=formats)

        except Exception as e:
            return render_template("result.html", title="Error", formats=[], error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
