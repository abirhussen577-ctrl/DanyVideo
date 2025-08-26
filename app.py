from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

# Phone's Downloads folder
DOWNLOAD_FOLDER = os.path.expanduser('~/storage/downloads')

# Cookies files for different platforms
COOKIES = {
    "youtube.com": "cookies/youtube.txt",
    "youtu.be": "cookies/youtube.txt",
    "facebook.com": "cookies/fb.txt",
    "fb.watch": "cookies/fb.txt",
    "instagram.com": "cookies/ig.txt",
    "tiktok.com": "cookies/tiktok.txt"
}

def get_cookie_file(url):
    for domain, path in COOKIES.items():
        if domain in url:
            return path
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    if not url:
        return '❌ No URL provided', 400

    # File name format: video title + id
    outtmpl = os.path.join(DOWNLOAD_FOLDER, '%(title).80s-%(id)s.%(ext)s')

    # Get correct cookie file based on URL
    cookie_file = get_cookie_file(url)

    ydl_opts = {
        'format': 'bv*+ba/b',
        'outtmpl': outtmpl,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'restrictfilenames': True
    }

    if cookie_file and os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return f"✅ Download complete! File is available in: {DOWNLOAD_FOLDER}"
    except Exception as e:
        return f"❌ Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
