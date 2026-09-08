import os
import sqlite3
from typing import Optional

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./calls.db")
# We'll parse sqlite path to simple file path for sqlite3
if DB_PATH.startswith("sqlite:///"):
    DB_FILE = DB_PATH.replace("sqlite:///", "")
else:
    DB_FILE = DB_PATH

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS calls (
    id TEXT PRIMARY KEY,
    filename TEXT,
    customer TEXT,
    status TEXT,
    transcript TEXT,
    summary TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

_conn = get_conn()
_conn.execute(CREATE_TABLE_SQL)
_conn.commit()

import datetime

def save_call_entry(call_id: str, filename: str, customer: Optional[str]):
    now = datetime.datetime.utcnow().isoformat()
    _conn.execute(
        "INSERT INTO calls (id, filename, customer, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (call_id, filename, customer, "uploaded", now, now),
    )
    _conn.commit()

def update_call_status(call_id: str, status: str):
    now = datetime.datetime.utcnow().isoformat()
    _conn.execute(
        "UPDATE calls SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, call_id),
    )
    _conn.commit()

def save_transcript_and_summary(call_id: str, transcript: str, summary: str):
    now = datetime.datetime.utcnow().isoformat()
    _conn.execute(
        "UPDATE calls SET transcript = ?, summary = ?, status = ?, updated_at = ? WHERE id = ?",
        (transcript, summary, "done", now, call_id),
    )
    _conn.commit()

def get_call(call_id: str):
    cur = _conn.execute("SELECT id, filename, customer, status, transcript, summary, created_at, updated_at FROM calls WHERE id = ?", (call_id,))
    row = cur.fetchone()
    if not row:
        return None
    keys = ["id","filename","customer","status","transcript","summary","created_at","updated_at"]
    return dict(zip(keys, row))
