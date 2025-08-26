from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url', '').strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'bv*+ba/b',
        'noplaylist': True,
        'restrictfilenames': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title")
            thumbnail = info.get("thumbnail")

            # collect formats
            formats = []
            for f in info["formats"]:
                if not f.get("url"):
                    continue
                fmt_note = f.get("format_note") or (str(f.get("height")) + "p" if f.get("height") else "Audio")
                ext = f.get("ext")
                resolution = f.get("height") or 0
                formats.append({
                    "format": fmt_note,
                    "ext": ext,
                    "resolution": resolution,
                    "url": f["url"]
                })

            # sort High → Low
            formats = sorted(formats, key=lambda x: x["resolution"] if x["resolution"] else 0, reverse=True)

        return jsonify({
            "title": title,
            "thumbnail": thumbnail,
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
