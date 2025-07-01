from flask import Flask, request, send_file
from flask_cors import CORS
import os
from converters.img_converter import convert_image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return {"status": "API running"}

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files['file']
    output_format = request.form['format']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    output_path = convert_image(input_path, output_format)
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
