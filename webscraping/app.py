"""
Flask UI to browse, search and visualise the scraped products.

Run:  python app.py   ->  http://127.0.0.1:5000
"""
import os
import sqlite3

from flask import Flask, render_template, request

import visualize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "products.db")
PER_PAGE = 20

app = Flask(__name__)


def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def db_ready():
    return os.path.exists(DB_PATH)


@app.route("/")
def index():
    if not db_ready():
        return render_template("index.html", missing_data=True, products=[], total=0, args={}, page=1, pages=1)

    q = request.args.get("q", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_rating = request.args.get("min_rating", type=int)
    sort = request.args.get("sort", "title")
    page = max(request.args.get("page", 1, type=int), 1)

    where, params = [], []
    if q:
        where.append("(title LIKE ? OR description LIKE ? OR category LIKE ?)")
        params += [f"%{q}%"] * 3
    if min_price is not None:
        where.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        where.append("price <= ?")
        params.append(max_price)
    if min_rating:
        where.append("rating >= ?")
        params.append(min_rating)
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    order = {
        "title": "title ASC",
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "rating": "rating DESC, title ASC",
    }.get(sort, "title ASC")

    total = query_db(f"SELECT COUNT(*) AS n FROM products {clause}", params)[0]["n"]
    pages = max((total + PER_PAGE - 1) // PER_PAGE, 1)
    page = min(page, pages)
    products = query_db(
        f"SELECT * FROM products {clause} ORDER BY {order} LIMIT ? OFFSET ?",
        params + [PER_PAGE, (page - 1) * PER_PAGE],
    )
    args = {k: v for k, v in request.args.items() if k != "page"}
    return render_template("index.html", products=products, total=total, page=page,
                           pages=pages, args=args, missing_data=False)


@app.route("/charts")
def charts():
    if not db_ready():
        return render_template("charts.html", charts=[], missing_data=True)
    names = visualize.make_all()
    return render_template("charts.html", charts=names, missing_data=False)


if __name__ == "__main__":
    app.run(debug=True)
