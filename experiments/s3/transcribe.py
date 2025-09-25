from yt_dlp import YoutubeDL

URLS = ['https://youtu.be/1yMozrDEqbg']
with YoutubeDL() as ydl:
    ydl.download(URLS)