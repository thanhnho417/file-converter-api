import yt_dlp
import os


    
def youtubedl(url, quality, ytdlp_progress_hook):
    format_url = ''
    if quality == 'Tối đa' or quality == 'Maximum' or quality == 'max':
        format_url = 'bestvideo+bestaudio/best'
    else:
        format_url = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    output_dỉr = 'tempfile'
    os.makedirs(output_dỉr, exist_ok=True)
    ydl_opts = {
        'format': format_url,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_dỉr, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'progress_hooks': [ytdlp_progress_hook],
        'quiet': True,
        'geo-bypass': True,
        'geo_bypass_country': 'VN'
        
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")  # fallback
        return filename
    