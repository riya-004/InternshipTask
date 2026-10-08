"""
Flask web app: upload an image, see detected text regions and the extracted text.

Run:  python app.py   ->  http://127.0.0.1:5000
Requires the Tesseract engine installed on your machine (see README).
"""
import os
import uuid

import pytesseract
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from ocr_engine import run_ocr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED = {"png", "jpg", "jpeg", "bmp", "tif", "tiff", "webp"}

# Windows users: uncomment and fix the path if Tesseract is not on PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    file = request.files.get("image")
    if not file or not file.filename:
        return render_template("index.html", error="Please choose an image file.")
    if not allowed(file.filename):
        return render_template("index.html", error="Unsupported file type. Use PNG, JPG, BMP, TIFF or WEBP.")

    token = uuid.uuid4().hex[:10]
    name = f"{token}_{secure_filename(file.filename)}"
    path = os.path.join(UPLOAD_DIR, name)
    file.save(path)

    try:
        result = run_ocr(path)
    except pytesseract.TesseractNotFoundError:
        return render_template("index.html", error="Tesseract is not installed or not on PATH. See the README.")
    except Exception as exc:  # corrupt image etc.
        return render_template("index.html", error=f"Could not process image: {exc}")

    annotated_name = f"{token}_annotated.png"
    result["annotated"].save(os.path.join(UPLOAD_DIR, annotated_name))
    return render_template("index.html", text=result["text"], regions=result["regions"],
                           original=name, annotated=annotated_name)


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
