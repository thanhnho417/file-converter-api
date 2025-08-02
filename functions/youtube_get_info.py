from googleapiclient.discovery import build
import re
from urllib.parse import urlparse, parse_qs


api_key = 'AIzaSyDUd-Tvpub-Fz4FNxKU_CYvWz9Qv20149o'
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_url(video_url):
    parse_url = urlparse(video_url)
    if parse_url.hostname in ['www.youtube.com','youtube.com']:
        if parse_url.path == '/watch':
            query = parse_qs(parse_url.query)
            return query.get('v', [None])[0]
        elif parse_url.path.startswith('/embed/'):
            return parse_url.path.split('/embed/')[1]
        elif parse_url.path.startswith('/shorts/'):
            return parse_url.path.split('/shorts/')[1]
    
    elif parse_url.hostname == 'youtu.be':
        return parse_url.path.strip('/')
    
    return None


def youtube_video_info(video_id):
    ytrequest = youtube.videos().list(
        part = "snippet, contentDetails, statistics",
        id=video_id
    )
    best_thumbnail = ''
    ytresponse = ytrequest.execute()
    
    if not ytresponse:
        print("Không phát hiện video")
        return None
    
    ytvideo = ytresponse['items'][0]
    ytsnippet = ytvideo['snippet']
    ytstat = ytvideo['statistics']
    ytthumbnails = ytsnippet.get('thumbnails', {})
    
    thumbnail_priority = ['maxres', 'standard', 'high', 'medium', 'default']
    for quality in thumbnail_priority:
        if quality in ytthumbnails:
            best_thumbnail = ytthumbnails[quality]['url']
            break
    
    ytvideoinfo = {
        'title': ytsnippet['title'],
        'description': ytsnippet['description'],
        'published_at': ytsnippet['publishedAt'],
        'channel_title': ytsnippet['channelTitle'],
        'view_count': ytstat.get('viewCount', 0),
        'like_count': ytstat.get('likeCount', 0),
        'comment_count': ytstat.get('commentCount', 0),
        'best_thumbnail_url': best_thumbnail
    }
    return ytvideoinfo


video_id = str(input("Nhập URL: "))

youtube_key = extract_url(video_id)

video_info = youtube_video_info(youtube_key)

if video_info:
    print(f"Tiêu đề: {video_info['title']}")
    print(f"Kênh: {video_info['channel_title']}")
    print(f"Xuất bản vào: {video_info['published_at']}")
    print(f"Ảnh thumbnails: {video_info['best_thumbnail_url']}")





