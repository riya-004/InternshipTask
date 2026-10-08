# Internship Project Tasklist

Two small projects, each with its own Flask web app:

1. **Web scraping (e-commerce)** - scrape products, store them, visualise trends, search them in a web UI
2. **Text detection and extraction (OCR)** - detect and extract text from images with Tesseract

```
internship-project/
├── requirements.txt
├── webscraping/
│   ├── scraper.py        # scrapes products -> SQLite + Excel
│   ├── visualize.py      # Matplotlib / Seaborn charts
│   ├── app.py            # Flask UI: search, filter, sort, charts
│   ├── templates/
│   └── data/             # products.db and products.xlsx (created by the scraper)
└── ocr/
    ├── ocr_engine.py     # Tesseract: preprocess, detect regions, extract text
    ├── app.py            # Flask UI: upload image, show boxes + text
    ├── templates/
    └── sample_images/    # sample images for testing
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The OCR task also needs the **Tesseract engine** (separate from the Python package):

- Windows: install from https://github.com/UB-Mannheim/tesseract/wiki, then set `tesseract_cmd` in `ocr/app.py` (a commented line is provided)
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt install tesseract-ocr`

## Task 01 - Web scraping

Target site: [books.toscrape.com](https://books.toscrape.com), a demo e-commerce store made for scraping practice.

```bash
cd webscraping
python scraper.py                 # 50 pages, 1000 products (title, price, rating, availability)
python scraper.py --details       # also category + description (visits every product page, slower)
python scraper.py --max-pages 5   # quick run
python app.py                     # open http://127.0.0.1:5000
```

| Requirement | Where |
|---|---|
| Scrape title, rating, price, description | `scraper.py` (requests + BeautifulSoup) |
| Store in Excel or database | `data/products.db` (SQLite) and `data/products.xlsx` |
| Visualise trends (Matplotlib, Seaborn) | `visualize.py`, shown on the **Charts** page |
| Search functionality | search box + price / rating filters + sorting in the UI |
| Simple UI with Flask | `app.py` + `templates/` |

## Task 02 - Text detection and extraction

```bash
cd ocr
python app.py                     # open http://127.0.0.1:5000 and upload an image
python ocr_engine.py sample_images/sample.png   # or use the engine from the command line
```

| Requirement | Where |
|---|---|
| Dataset of images / scanned documents | `sample_images/` |
| OCR engine to detect text regions (Tesseract) | `ocr_engine.py` - `detect_regions()` |
| Extract text from detected regions | `ocr_engine.py` - `extract_text()` |
| Flask app to upload images and show text | `app.py` + `templates/index.html` |

Images are preprocessed (orientation fix, grayscale, auto-contrast, upscaling) before OCR to improve accuracy.
