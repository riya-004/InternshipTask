"""
Task 02 - Text detection and extraction with Tesseract OCR.

- detect_regions(): finds text regions (word boxes) with Tesseract
- extract_text():  returns the text found in the image
- annotate():      draws the detected boxes on a copy of the image
"""
import pytesseract
from PIL import Image, ImageDraw, ImageOps

MIN_CONFIDENCE = 40  # ignore very uncertain detections


def preprocess(image):
    """Fix orientation, convert to grayscale, boost contrast and upscale small images."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    if gray.width < 1000:
        scale = 1000 / gray.width
        gray = gray.resize((int(gray.width * scale), int(gray.height * scale)), Image.LANCZOS)
    return image, gray


def detect_regions(gray, lang="eng"):
    """Return a list of dicts: text, confidence and bounding box of each detected word."""
    data = pytesseract.image_to_data(gray, lang=lang, output_type=pytesseract.Output.DICT)
    regions = []
    for i, text in enumerate(data["text"]):
        text = text.strip()
        try:
            conf = float(data["conf"][i])
        except ValueError:
            conf = -1
        if text and conf >= MIN_CONFIDENCE:
            regions.append({
                "text": text,
                "confidence": round(conf, 1),
                "left": data["left"][i], "top": data["top"][i],
                "width": data["width"][i], "height": data["height"][i],
            })
    return regions


def extract_text(gray, lang="eng"):
    return pytesseract.image_to_string(gray, lang=lang).strip()


def annotate(gray, regions):
    """Draw a green box around every detected text region."""
    img = gray.convert("RGB")
    draw = ImageDraw.Draw(img)
    thickness = max(2, img.width // 400)
    for r in regions:
        box = [r["left"], r["top"], r["left"] + r["width"], r["top"] + r["height"]]
        draw.rectangle(box, outline=(0, 200, 70), width=thickness)
    return img


def run_ocr(path, lang="eng"):
    original, gray = preprocess(Image.open(path))
    regions = detect_regions(gray, lang)
    return {
        "text": extract_text(gray, lang),
        "regions": regions,
        "annotated": annotate(gray, regions),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python ocr_engine.py <image>")
    result = run_ocr(sys.argv[1])
    print(result["text"])
    print(f"\n[{len(result['regions'])} text regions detected]")
