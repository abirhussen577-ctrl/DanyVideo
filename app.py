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
            fmt = {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("format_note") or f.get("height"),
                "filesize": f.get("filesize") or 0,
                "url": f.get("url")
            }
            formats.append(fmt)

        # Sort formats from high quality to low quality
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
            return 0

        formats = sorted(formats, key=sort_key, reverse=True)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
