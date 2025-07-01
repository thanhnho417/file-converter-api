import ffmpeg

def convert_audio(input_path, output_format):
    output_path = input_path.rsplit('.', 1)[0] + '.' + output_format
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path)
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print("STDERR:", e.stderr.decode())
        raise
    return output_path
