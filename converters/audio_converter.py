import ffmpeg

def convert_audio(input_path, output_format):
    output_path = input_path.rsplit('.', 1)[0] + '.' + output_format
    (
        ffmpeg
        .input(input_path)
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path
