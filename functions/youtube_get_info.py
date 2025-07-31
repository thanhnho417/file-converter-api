import yt_dlp

def yt_get_info_video(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as f:
        info = f.extract_info(url, download=False)
        
    title = info.get('title')
    duration = info.get('duration')
    thumbnail = info.get('thumbnail')
    return title, duration, thumbnail

def changetime(duration):
    x = int(duration)
    h = x//3600
    m = (x%3600)//60
    s = x % 60
    return f"{h}h {m}p {s}s"