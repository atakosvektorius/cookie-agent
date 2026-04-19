import os
import sqlite3

DB_PATH = os.getenv("DB_PATH")

TRACKED_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-embedder-policy",
    "cross-origin-resource-policy",
    "server",
    "x-powered-by",
    "x-aspnet-version",
    "x-aspnetmvc-version",
    "via",
    "x-powered-cms",
]


def _col(h):
    return h.replace("-", "_")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    header_cols = ",\n            ".join(f"{_col(h)} TEXT" for h in TRACKED_HEADERS)
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS domains_queue (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL
            )
        """)
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS scrape_results (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cookies TEXT,
                {header_cols}
            )
        """)


def fetch_fallback_domains(limit):
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute(
            "SELECT domain FROM domains_queue ORDER BY id LIMIT ?",
            (int(limit),),
        ).fetchall()
    return [r[0] for r in rows]


def _lookup(headers, name):
    target = name.lower()
    for k, v in headers.items():
        if k.lower() == target:
            return v
    return None


def upsert_result(domain, cookie_names, headers):
    header_cols = [_col(h) for h in TRACKED_HEADERS]
    header_vals = [_lookup(headers, h) for h in TRACKED_HEADERS]

    cols = ["domain", "scraped_at", "cookies", *header_cols]
    placeholders = ["?", "CURRENT_TIMESTAMP", "?", *(["?"] * len(header_cols))]
    values = [domain, ",".join(cookie_names), *header_vals]
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != "domain")

    sql = (
        f"INSERT INTO scrape_results ({', '.join(cols)}) "
        f"VALUES ({', '.join(placeholders)}) "
        f"ON CONFLICT(domain) DO UPDATE SET {updates}"
    )
    with sqlite3.connect(DB_PATH) as c:
        c.execute(sql, values)
