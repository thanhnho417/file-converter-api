import os
import io
import tempfile
import zipfile
import ffmpeg
from werkzeug.utils import secure_filename
import time

temp_dir = 'tempfile'
os.makedirs(temp_dir, exist_ok=True)

def save_temp_file(file):
    ext = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=temp_dir) as f:
        temp_path = f.name
    file.save(temp_path)
    return temp_path

def convert_with_ffmpeg(input_path, output_format, is_audio=True):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}', dir=temp_dir) as f:
        output_path = f.name
    
    try:
        stream = ffmpeg.input(input_path)
        if is_audio:
            if output_format == 'mp3':
                stream = ffmpeg.output(stream, output_path, format='mp3', acodec='libmp3lame', audio_bitrate='192k')
            elif output_format == 'flac':
                stream = ffmpeg.output(stream, output_path, format='flac', acodec='flac')
            elif output_format == 'wav':
                stream = ffmpeg.output(stream, output_path, format='wav', acodec='pcm_s16le')
            elif output_format == 'ogg':
                stream = ffmpeg.output(stream, output_path, format='ogg', acodec='libvorbis')
            else:
                raise Exception(f'Định dạng âm thanh không hỗ trợ: {output_format}')
        else:
            if output_format == 'mp4':
                stream = ffmpeg.output(stream, output_path, format='mp4', vcodec='libx264', acodec='aac')
            elif output_format == 'mkv':
                stream = ffmpeg.output(stream, output_path, format='matroska', vcodec='libx264', acodec='aac')
            elif output_format == '3gp':
                stream = ffmpeg.output(stream, output_path, format='3gp', vcodec='h263', acodec='aac')
            elif output_format == 'ogg':
                stream = ffmpeg.output(stream, output_path, format='ogg', vcodec='libtheora', acodec='libvorbis')
            else:
                raise Exception(f'Định dạng video không hỗ trợ: {output_format}')

        
        ffmpeg.run(stream, quiet=True, overwrite_output=True)
        
        with open(output_path, 'rb') as f:
            return io.BytesIO(f.read())
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error: {e.stderr.decode()}") from e
    finally:
        safe_remove(input_path)
        safe_remove(output_path)

def convert_single(file, output_format, is_audio=True):
    input_path = save_temp_file(file)
    return convert_with_ffmpeg(input_path, output_format, is_audio=is_audio)

def convert_multiple(files, output_format, is_audio=True):
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            try:
                name_wo_ext = os.path.splitext(secure_filename(file.filename))[0]
                input_path = save_temp_file(file)
                convert_io = convert_with_ffmpeg(input_path, output_format, is_audio=is_audio)
                zip_file.writestr(f'{name_wo_ext}.{output_format}', convert_io.read())
            except Exception as e:
                # Ghi lại lỗi nhưng tiếp tục với các file khác
                print(f"Error processing file {file.filename}: {str(e)}")
                continue
    zip_io.seek(0)
    return zip_io            

def safe_remove(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f'Không thể xóa file {path}: {e}')
        
def cleanup_temp_file(max_second=3600):
    now = time.time()
    for file in os.listdir(temp_dir):
        path = os.path.join(temp_dir, file)
        if os.path.isfile(path):
            age = now - os.path.getmtime(path)
            if age > max_second:
                safe_remove(path)