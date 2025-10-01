from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import threading
import time
import os
import re
import json
from functions.media_converter import (
    convert_single,
    convert_multiple,
    cleanup_temp_file
)

from functions.youtubedl import youtubedl
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

mainserver = 'https://fantastic-memory-pxr7pxg9q47h45x-5000.app.github.dev/'

# Các định dạng được hỗ trợ
SUPPORTED_FORMATS = {
    'audio': ['mp3', 'flac', 'wav', 'ogg'],
    'video': ['mp4', 'mkv', '3gp']
}

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text or '')


@app.route('/testmedia')
def welcome():
    media_dir = os.path.dirname(__file__)
    media_path = os.path.join(media_dir, 'functions', 'assets', 'videos.json')
    raw_title = request.args.get('id') or ''
    target = str(raw_title.strip().lower())
    if not target:
        return jsonify({'Lỗi': 'Không có id'})
    with open(media_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        matches = []
    for movie in data:
        if target == 'all':
            return jsonify(data)
        media_title = movie.get('title', '')
        if media_title and target in media_title.lower():
            matches.append(movie)
    if len(matches) >= 1:
        return jsonify(matches)
    
    return jsonify({'error': 'kb'}), 400




@app.route('/')
def home():
    return jsonify({
        'status': 'ready',
        'message': 'Ready to break'
    })


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
    app.run(host='0.0.0.0', port=5000, debug=True)
