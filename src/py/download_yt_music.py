import os
import yt_dlp

def download_playlist_as_mp3():
    download_path = r"/mnt/c/Users/JiaoYuan/Music"
    playlist_url = "https://www.youtube.com/watch?v=Nk9ztUjikT0&list=PLwqG5QrBfRXlq3fMjMQD3ga-Z7wKPw7FD"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s - %(artist)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }, {
            'key': 'EmbedThumbnail',
        }, {
            'key': 'FFmpegMetadata',
        }],
        'ignoreerrors': True,
        'download_archive': os.path.join(download_path, 'downloaded_songs.txt')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

if __name__ == '__main__':
    download_playlist_as_mp3()