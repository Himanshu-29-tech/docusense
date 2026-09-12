import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect("docusense.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            document_type TEXT,
            raw_text TEXT,
            entities TEXT,
            summary TEXT,
            anomalies TEXT,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_document(filename, document_type, raw_text, entities, summary, anomalies):
    conn = sqlite3.connect("docusense.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (filename, document_type, raw_text, entities, summary, anomalies, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        filename, document_type, raw_text,
        json.dumps(entities), summary, json.dumps(anomalies),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_documents():
    conn = sqlite3.connect("docusense.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY processed_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def check_duplicate_invoice(invoice_number: str) -> bool:
    conn = sqlite3.connect("docusense.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents WHERE entities LIKE ?", (f'%{invoice_number}%',))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0