from flask import Flask, request, jsonify, Response
import os
import yt_dlp

app = Flask(__name__)

@app.route('/get_info', methods=['POST'])
def get_info():
    try:
        data = request.get_json()
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Detect which site it is and load cookies
        cookies_file = None
        if "youtube.com" in url or "youtu.be" in url:
            cookies_file = "cookies/youtube.txt"
        elif "facebook.com" in url:
            cookies_file = "cookies/fb.txt"
        elif "instagram.com" in url:
            cookies_file = "cookies/ig.txt"
        elif "tiktok.com" in url:
            cookies_file = "cookies/tiktok.txt"

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'cookies': cookies_file if cookies_file and os.path.exists(cookies_file) else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if not f.get("url"):
                continue
            filesize_mb = round(f.get("filesize", 0) / 1024 / 1024, 2) if f.get("filesize") else None
            fmt = {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("format_note") or f.get("height") or "Unknown",
                "filesize_mb": filesize_mb if filesize_mb else "Unknown",
                "url": f.get("url")
            }
            formats.append(fmt)

        # Sort formats from high to low quality
        def sort_key(f):
            res = f.get("resolution")
            if isinstance(res, int):
                return res
            if isinstance(res, str) and res.isdigit():
                return int(res)
            if isinstance(res, str) and "p" in res:
                try:
                    return int(res.replace("p", ""))
                except:
                    return 0
            return -1  # Audio or unknown formats go last

        formats = sorted(formats, key=sort_key, reverse=True)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Failed to fetch video: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/download_file', methods=['POST'])
def download_file():
    try:
        data = request.form
        url = data.get("url", "").strip()
        format_id = data.get("format_id", "").strip()
        if not url or not format_id:
            return jsonify({"error": "URL or format ID missing"}), 400

        ydl_opts = {
            'quiet': True,
            'format': format_id,
            'outtmpl': '-',  # Stream to stdout
            'cookies': "cookies/youtube.txt" if "youtube.com" in url or "youtu.be" in url else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}".replace('/', '_').replace('\\', '_')
            video_data = ydl.process_ie_result(info, download=True)

        return Response(
            video_data,
            mimetype='video/mp4',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',
