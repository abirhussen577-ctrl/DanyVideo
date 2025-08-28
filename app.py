from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please enter a URL")
        
        # yt-dlp দিয়ে ভিডিও ফরম্যাট ফেচ করা
        ydl_opts = {"listformats": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        return render_template("result.html", info=info)
    return render_template("index.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
