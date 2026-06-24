#!/usr/bin/env python3
"""
Tellofix XDCC Searcher - Search API
All config via environment variables. Copy .env.example to .env first.
"""

import os
import time
import requests
import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host":        os.environ.get("MYSQL_HOST", "db"),
    "user":        os.environ.get("MYSQL_USER", "xdcc"),
    "password":    os.environ.get("MYSQL_PASSWORD", ""),
    "database":    os.environ.get("MYSQL_DATABASE", "xdcc_downloader"),
    "charset":     "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

GERMAN_KEYWORDS = [
    "german", "deutsch", "ger.", ".ger.", "deu.", ".deu.",
    "dl.", "ac3dl", "ddp.dl", "dd+dl", "german.dl",
    "german.ac3", "german.aac", "german.dts",
]

def is_german(filename):
    fname = filename.lower()
    return any(kw in fname for kw in GERMAN_KEYWORDS)

def get_db():
    return pymysql.connect(**DB_CONFIG)

@app.route("/search")
def search():
    query       = request.args.get("q", "").strip()
    german_only = request.args.get("german", "true").lower() == "true"
    page        = max(1, int(request.args.get("page", 1)))
    per_page    = 20
    offset      = (page - 1) * per_page

    if not query:
        return jsonify({"results": [], "total": 0, "page": page})

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT network, channel, bot, pack_number, file_size, filename
                   FROM irc_packs
                   WHERE filename LIKE %s
                   ORDER BY id DESC
                   LIMIT %s OFFSET %s""",
                (f"%{query}%", per_page + 1, offset)
            )
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e), "results": [], "total": 0}), 500

    if german_only:
        rows = [r for r in rows if is_german(r["filename"])]

    has_next = len(rows) > per_page
    return jsonify({"results": rows[:per_page], "page": page, "has_next": has_next})

@app.route("/scrape/sunxdcc")
def scrape_sunxdcc():
    query       = request.args.get("q", "").strip()
    german_only = request.args.get("german", "true").lower() == "true"
    if not query:
        return jsonify({"results": []})
    try:
        url  = f"https://sunxdcc.com/deliver.php?sterm={requests.utils.quote(query)}&Submit=Search"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = []
        for tr in soup.select("table tr")[1:]:
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cols) >= 6:
                rows.append({
                    "network": cols[0], "channel": cols[1], "bot": cols[2],
                    "pack_number": cols[3], "file_size": cols[4], "filename": cols[5],
                })
        if german_only:
            rows = [r for r in rows if is_german(r["filename"])]
        return jsonify({"results": rows})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

@app.route("/scrape/xdcceu")
def scrape_xdcceu():
    query       = request.args.get("q", "").strip()
    german_only = request.args.get("german", "true").lower() == "true"
    if not query:
        return jsonify({"results": []})
    try:
        url  = f"https://www.xdcc.eu/search.php?searchkey={requests.utils.quote(query)}"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = []
        for tr in soup.select("table.searchresults tr")[1:]:
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cols) >= 6:
                rows.append({
                    "network": cols[0], "channel": cols[1], "bot": cols[2],
                    "pack_number": cols[3], "file_size": cols[4], "filename": cols[5],
                })
        if german_only:
            rows = [r for r in rows if is_german(r["filename"])]
        return jsonify({"results": rows})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=False)
