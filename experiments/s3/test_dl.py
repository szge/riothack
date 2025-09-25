import yt_dlp

URLS = ['https://www.youtube.com/watch?v=qf27qzFKv60']

ydl_opts = {
    'format': 'm4a/worstaudio/worst',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(URLS)