from pdf2image import convert_from_path

def convert_pdf(input_path):
    images = convert_from_path(input_path)
    output_paths = []
    for i, img in enumerate(images):
        out_path = input_path.rsplit('.', 1)[0] + f'_page{i+1}.png'
        img.save(out_path, 'PNG')
        output_paths.append(out_path)
    return output_paths
