from PIL import Image

def convert_image(input_path, output_format):
    img = Image.open(input_path)
    output_path = input_path.rsplit('.', 1)[0] + '.' + output_format
    img.save(output_path)
    return output_path
