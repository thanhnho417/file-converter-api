from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import threading
import time
import os

from functions.media_converter import (
    convert_single,
    convert_multiple,
    cleanup_temp_file
)

app = Flask(__name__)
CORS(app)

# Các định dạng được hỗ trợ
SUPPORTED_FORMATS = {
    'audio': ['mp3', 'flac', 'wav', 'ogg'],
    'video': ['mp4', 'mkv', '3gp']
}

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

if __name__ == '__main__':
    os.makedirs('tempfile', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
