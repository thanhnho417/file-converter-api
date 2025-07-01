import subprocess
import os

def convert_video(input_path, output_format):
    output_path = input_path.rsplit('.', 1)[0] + '.' + output_format
    subprocess.call(['ffmpeg', '-i', input_path, output_path])
    return output_path
