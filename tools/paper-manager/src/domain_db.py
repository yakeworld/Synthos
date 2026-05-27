"""Domain health tracking for Sci-Hub mirrors (SQLite-backed)."""
import sqlite3, threading, time, os
from pathlib import Path

_local = threading.local()
_DB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '.domain_cache')
_DB_PATH = os.path.join(_DB_DIR, 'domain_stats.db')

_SCHEMA = """
CREATE TABLE IF NOT EXISTS domain_stats (
    domain      TEXT PRIMARY KEY,
    success     INTEGER NOT NULL DEFAULT 0,
    fail        INTEGER NOT NULL DEFAULT 0,
    fail_streak INTEGER NOT NULL DEFAULT 0,
    avg_latency REAL,
    reachable   INTEGER NOT NULL DEFAULT 1,
    updated_at  REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS probe_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

def _get_conn():
    conn = getattr(_local, 'conn', None)
    if conn is None:
        os.makedirs(_DB_DIR, exist_ok=True)
        conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA)
        conn.commit()
        _local.conn = conn
    return conn

def load_stats():
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM domain_stats").fetchall()
    stats = {}
    for row in rows:
        stats[row['domain']] = {
            'success': row['success'], 'fail': row['fail'],
            'fail_streak': row['fail_streak'], 'reachable': row['reachable'],
            'avg_latency': row['avg_latency'], 'updated_at': row['updated_at'],
        }
    return stats

def update_probe(domain, ok, latency_ms):
    conn = _get_conn()
    now = time.time()
    existing = conn.execute("SELECT * FROM domain_stats WHERE domain=?", (domain,)).fetchone()
    if existing:
        s = existing['success'] + (1 if ok else 0)
        f = existing['fail'] + (0 if ok else 1)
        streak = 0 if ok else existing['fail_streak'] + 1
        conn.execute("""UPDATE domain_stats SET success=?, fail=?, fail_streak=?,
            avg_latency=?, reachable=?, updated_at=? WHERE domain=?""",
            (s, f, streak, latency_ms, 1 if ok else 0, now, domain))
    else:
        conn.execute("""INSERT INTO domain_stats (domain, success, fail, fail_streak,
            avg_latency, reachable, updated_at) VALUES (?,?,?,?,?,?,?)""",
            (domain, 1 if ok else 0, 0 if ok else 1, 0 if ok else 1,
             latency_ms, 1 if ok else 0, now))
    conn.commit()

def record_download_result(domain, success):
    conn = _get_conn()
    now = time.time()
    existing = conn.execute("SELECT * FROM domain_stats WHERE domain=?", (domain,)).fetchone()
    if existing:
        s = existing['success'] + (1 if success else 0)
        f = existing['fail'] + (0 if success else 1)
        streak = 0 if success else existing['fail_streak'] + 1
        conn.execute("UPDATE domain_stats SET success=?, fail=?, fail_streak=?, updated_at=? WHERE domain=?",
                     (s, f, streak, now, domain))
    else:
        conn.execute("INSERT INTO domain_stats (domain, success, fail, fail_streak, reachable, updated_at) VALUES (?,?,?,?,1,?)",
                     (domain, 1 if success else 0, 0 if success else 1, 0 if success else 1, now))
    conn.commit()

def get_probe_timestamp():
    conn = _get_conn()
    row = conn.execute("SELECT value FROM probe_meta WHERE key='last_probe'").fetchone()
    return float(row['value']) if row else 0

def set_probe_timestamp():
    conn = _get_conn()
    conn.execute("INSERT OR REPLACE INTO probe_meta (key, value) VALUES ('last_probe', ?)",
                 (str(time.time()),))
    conn.commit()

def get_best_domains(min_success_rate=0.3, limit=5):
    """Get best-performing domains, excluding those on cooldown."""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT domain, success, fail, fail_streak, avg_latency, reachable,
               CAST(success AS REAL) / MAX(success + fail, 1) as success_rate
        FROM domain_stats
        WHERE reachable = 1 AND fail_streak < 3
        ORDER BY success_rate DESC, avg_latency ASC
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_cooldown_domains():
    """Domains that failed >=3 times in a row, skipped temporarily."""
    conn = _get_conn()
    rows = conn.execute("SELECT domain FROM domain_stats WHERE fail_streak >= 3").fetchall()
    return [r['domain'] for r in rows]
