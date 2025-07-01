from pydub import AudioSegment

def convert_audio(input_path, output_format):
    audio = AudioSegment.from_file(input_path)
    output_path = input_path.rsplit('.', 1)[0] + '.' + output_format
    audio.export(output_path, format=output_format)
    return output_path
