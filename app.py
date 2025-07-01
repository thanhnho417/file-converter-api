from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from converters.img_converter import convert_image
from converters.audio_converter import convert_audio
from converters.video_converter import convert_video
from converters.pdf_converter import convert_pdf
from converters.ocr_converter import extract_text

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return {"status": "FFmpeg-based API running"}

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/convert/image", methods=["POST"])
def convert_img():
    file = request.files['file']
    output_format = request.form['format']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    output_path = convert_image(input_path, output_format)
    return send_file(output_path, as_attachment=True)

@app.route("/convert/audio", methods=["POST"])
def convert_aud():
    file = request.files['file']
    output_format = request.form['format']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    output_path = convert_audio(input_path, output_format)
    return send_file(output_path, as_attachment=True)

@app.route("/convert/video", methods=["POST"])
def convert_vid():
    file = request.files['file']
    output_format = request.form['format']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    output_path = convert_video(input_path, output_format)
    return send_file(output_path, as_attachment=True)

@app.route("/convert/pdf", methods=["POST"])
def convert_pdf_route():
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    image_paths = convert_pdf(input_path)
    return jsonify({"images": image_paths})

@app.route("/convert/ocr", methods=["POST"])
def convert_ocr():
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    result = extract_text(input_path)
    return jsonify({"text": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
