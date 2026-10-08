"""
Task 01 - Web scraping (e-commerce)

Scrapes product data (title, price, rating, availability, category, description)
from https://books.toscrape.com -- a demo e-commerce store built for scraping practice.
Data is saved to SQLite (data/products.db) and Excel (data/products.xlsx).

Usage:
    python scraper.py                    # scrape all 50 pages (1000 products)
    python scraper.py --max-pages 5      # scrape only the first 5 pages
    python scraper.py --details          # also open each product page for its description (slower)
"""
import argparse
import os
import re
import sqlite3
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "products.db")
XLSX_PATH = os.path.join(DATA_DIR, "products.xlsx")
HEADERS = {"User-Agent": "Mozilla/5.0 (internship-project scraper)"}
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_soup(session, url):
    resp = session.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def parse_price(text):
    """'£51.77' -> 51.77"""
    match = re.search(r"[\d.]+", text)
    return float(match.group()) if match else None


def scrape_details(session, url):
    """Open a product page and return (category, description)."""
    soup = get_soup(session, url)
    crumbs = soup.select("ul.breadcrumb li a")
    category = crumbs[-1].get_text(strip=True) if len(crumbs) >= 3 else None
    desc_tag = soup.select_one("#product_description + p")
    description = desc_tag.get_text(strip=True) if desc_tag else ""
    return category, description


def scrape(max_pages=50, details=False, delay=0.2):
    session = requests.Session()
    products = []
    for page in range(1, max_pages + 1):
        url = urljoin(BASE_URL, f"catalogue/page-{page}.html")
        try:
            soup = get_soup(session, url)
        except requests.HTTPError:
            break  # ran out of pages
        cards = soup.select("article.product_pod")
        if not cards:
            break
        for card in cards:
            link = urljoin(url, card.h3.a["href"])
            rating_word = card.select_one("p.star-rating")["class"][1]
            item = {
                "title": card.h3.a["title"],
                "price": parse_price(card.select_one("p.price_color").get_text()),
                "rating": RATING_MAP.get(rating_word),
                "availability": card.select_one("p.availability").get_text(strip=True),
                "url": link,
                "category": None,
                "description": "",
            }
            if details:
                item["category"], item["description"] = scrape_details(session, link)
                time.sleep(delay)
            products.append(item)
        print(f"Page {page}: {len(cards)} products (total {len(products)})")
        time.sleep(delay)
    return pd.DataFrame(products)


def save(df):
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("products", conn, if_exists="replace", index=False)
    df.to_excel(XLSX_PATH, index=False)
    print(f"Saved {len(df)} products -> {DB_PATH} and {XLSX_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-commerce product scraper")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--details", action="store_true",
                        help="visit each product page to get category + description")
    args = parser.parse_args()
    data = scrape(args.max_pages, args.details)
    if data.empty:
        raise SystemExit("No data scraped - check your internet connection.")
    save(data)
