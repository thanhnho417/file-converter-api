from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import threading
import time
import os
import yt_dlp
import re
from functions.media_converter import (
    convert_single,
    convert_multiple,
    cleanup_temp_file
)

from functions.youtubedl import youtubedl
from functions.youtube_get_info import changetime
app = Flask(__name__)
CORS(app)

mainserver = 'https://file-converter-api-ugp0.onrender.com'

# Các định dạng được hỗ trợ
SUPPORTED_FORMATS = {
    'audio': ['mp3', 'flac', 'wav', 'ogg'],
    'video': ['mp4', 'mkv', '3gp']
}

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text or '')

@app.route('/')
def home():
    return jsonify({
        'status': 'ready',
        'message': 'Ready to break'
    })

@app.route('/ytcheck', methods=['POST'])
def ytcheck():
    yturl = request.form.get('url')
    if not yturl: return 'Không phát hiện url', 400
    try:
        yfl_opts = {
            'quiet': True,
            'skip_download': True,
            'geo_bypass': True,
            'youtube_include_dash_manifest': False
        }
        with yt_dlp.YoutubeDL(yfl_opts) as f:
            ytinfo = f.extract_info(yturl, download = False)
            title = ytinfo.get('title')
            duration = ytinfo.get('duration')
            thumbnail = ytinfo.get('thumbnail')
            ytformats = ytinfo.get('formats', [])
            
        video_format = []
        best_audio = None
        best_audio_bitrates = 0
        seen_labels = set()
        for f in ytformats:
            if f.get('vcodec') != 'none':
                note = f.get('height')
                if not note:
                    continue
                label = f"{note}p"
                value = str(note)
                if label in seen_labels: continue
                seen_labels.add(label)
                video_format.append({
                    "format_id": f["format_id"],
                    "label": label,
                    'value': value
                })
            elif f.get('acodec') != "none" and f.get('vcodec') == 'none':
                abr = f.get('abr', 0)
                if abr is not None and abr > best_audio_bitrates:
                    best_audio_bitrates = abr
                    best_audio = f
        html = f'<form class="ytdlp" method="POST" action="{mainserver}/ytdlp">'
        html+= f'<input type="hidden" name="url" value="{yturl}">'
        html+= f'<input type="hidden" name="title" value="{title}">'
        htmlytselect = '<div class="ytdlpoption">'
        htmlytselect += '<label for="ytqualityselect">Chọn chất lượng:</label>'
        htmlytselect += '<select name="ytqualityselect">'
        htmlytselect += '<option value="" disable selected>Chọn chất lượng</option>'
        for vf in video_format:
            htmlytselect += f'<option value="{vf["value"]}">{vf["label"]}</option>'
        
        htmlytselect += '</select></div>'
        html += htmlytselect
        html += '<button type="submit">Tải</button></form>'
            
        return f"""
        <div class="yt-checked-info">
            <img src="{thumbnail}" alt="ytimg" width="30%">
            <div class="yt-check-info-title" style="width:70%; text-align: start">
                <p style="font-weight: bold">{title}</p>
                <p>Thời lượng: {changetime(duration)}</p>
            </div>
            
        </div>
        {html}
        
        """
    except Exception as e:
        return f"<p style='color:red'>Lỗi kiểm tra: {str(e)}</p>", 500


@app.route('/ytdlp', methods=['POST'])
def ytdlpset():
    url = request.form.get('url')
    quality = request.form.get('ytqualityselect')
    try:
        file_path = youtubedl(url, quality, ytdlp_progress_hook)
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path), mimetype='video/mp4')
    except Exception as e:
        return f'<p style="color:red">❌ Lỗi: {str(e)}</p>', 500



@app.route('/convert', methods=['POST'])
def convert_media():
    files = request.files.getlist('files')
    tar_format = request.form.get('format', '').lower()
    media_type = request.form.get('type', 'audio').lower()

    # Xác định có phải audio hay không
    is_audio = media_type == 'audio'

    # Kiểm tra hợp lệ
    if not files or not tar_format:
        return jsonify({'error': 'Thiếu file hoặc định dạng đầu ra'}), 400

    if media_type not in SUPPORTED_FORMATS:
        return jsonify({'error': f'Loại media không được hỗ trợ: {media_type}'}), 400

    if tar_format not in SUPPORTED_FORMATS[media_type]:
        return jsonify({'error': f'Định dạng {tar_format} không hỗ trợ cho loại {media_type}'}), 400

    try:
        if len(files) == 1:
            output_io = convert_single(files[0], tar_format, is_audio=is_audio)
            return send_file(
                output_io,
                as_attachment=True,
                download_name=f'converted.{tar_format}',
                mimetype=f'{media_type}/{tar_format}'
            )
        else:
            zip_io = convert_multiple(files, tar_format, is_audio=is_audio)
            return send_file(
                zip_io,
                as_attachment=True,
                download_name='media_converted_file.zip',
                mimetype='application/zip'
            )
    except Exception as e:
        return jsonify({'error': f'Lỗi khi chuyển đổi: {str(e)}'}), 500

# Tự động xóa file tạm sau 1 giờ
def schedule_cleanup():
    while True:
        cleanup_temp_file(max_second=3600)
        time.sleep(3600)

threading.Thread(target=schedule_cleanup, daemon=True).start()

def ytdlp_progress_hook(d):
    if d.get('status') == 'downloading':
        ytdlpstatus['percent'] = strip_ansi(d.get('_percent_str', '').strip())
        ytdlpstatus['speed'] = strip_ansi(d.get('_speed_str', '').strip())
        ytdlpstatus['eta'] = strip_ansi(d.get('_eta_str', '').strip())
    return 'Không có tiến trình tải'
ytdlpstatus = {'percent': '0%', 'speed': '', 'eta': ''}
@app.route('/ytprogress')
def ytgetprogress():
    return jsonify(ytdlpstatus)


if __name__ == '__main__':
    os.makedirs('tempfile', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
