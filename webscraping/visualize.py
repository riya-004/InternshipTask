"""
Visualize trends in the scraped product data with Matplotlib and Seaborn.
Charts are saved as PNGs in static/charts/ and shown on the Flask "Charts" page.

Usage:  python visualize.py
"""
import os
import sqlite3

import matplotlib

matplotlib.use("Agg")  # no GUI needed
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "products.db")
CHART_DIR = os.path.join(BASE_DIR, "static", "charts")

sns.set_theme(style="whitegrid", palette="deep")


def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM products", conn)


def _save(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, name), dpi=130)
    plt.close(fig)


def price_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(df["price"], bins=25, kde=True, ax=ax)
    ax.set_title("Price distribution")
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Number of products")
    _save(fig, "price_distribution.png")


def rating_counts(df):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(x="rating", data=df, ax=ax)
    ax.set_title("Products per star rating")
    ax.set_xlabel("Rating (stars)")
    ax.set_ylabel("Number of products")
    _save(fig, "rating_counts.png")


def price_by_rating(df):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(x="rating", y="price", data=df, ax=ax)
    ax.set_title("Price vs. rating")
    ax.set_xlabel("Rating (stars)")
    ax.set_ylabel("Price (£)")
    _save(fig, "price_by_rating.png")


def avg_price_by_category(df):
    if df["category"].notna().sum() == 0:
        return  # categories only exist when scraped with --details
    top = (df.dropna(subset=["category"]).groupby("category")["price"]
           .agg(["mean", "count"]).query("count >= 3")
           .sort_values("mean", ascending=False).head(12))
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top["mean"], y=top.index, ax=ax)
    ax.set_title("Average price by category (top 12)")
    ax.set_xlabel("Average price (£)")
    ax.set_ylabel("")
    _save(fig, "avg_price_by_category.png")


def make_all():
    df = load_data()
    price_distribution(df)
    rating_counts(df)
    price_by_rating(df)
    avg_price_by_category(df)
    return sorted(os.listdir(CHART_DIR))


if __name__ == "__main__":
    print("Created:", make_all())
