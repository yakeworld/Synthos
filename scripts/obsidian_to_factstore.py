#!/usr/bin/env python3
"""Sync Obsidian vault → fact_store: extract key facts from modified notes.

Scans the Synthos vault for recently modified markdown files (within N hours)
and extracts structured facts to store in the holographic memory.

Usage:
  python3 obsidian_to_factstore.py              # sync last 24h changes
  python3 obsidian_to_factstore.py --hours 48   # custom window
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
VAULT_PATH = os.path.expanduser("~/Synthos")
MEMORY_DB = os.path.expanduser("~/.hermes/memory_store.db")

# Patterns to extract facts from markdown content
_FACT_PATTERNS = [
    # Table rows with key-value data (e.g. experiment results)
    re.compile(r'\|\s*(\w[\w\s/+-]+?)\s*\|\s*([\d.+-]+%?)\s*\|'),
    # Bold-wrapped key terms: **key**: value
    re.compile(r'\*\*([^*]+)\*\*\s*:\s*([^\n]+)'),
    # Tags in YAML frontmatter
    re.compile(r'^tags:\s*\[(.+)\]', re.MULTILINE),
]

_SECTION_HEADER = re.compile(r'^## (.+)$', re.MULTILINE)
_RE_CJK = re.compile(r'[\u4e00-\u9fff]')


def extract_facts(filepath: str, modified_ago_hours: float) -> list[dict]:
    """Extract fact-worthy content from a markdown note."""
    path = Path(filepath)
    if not path.exists() or path.suffix != '.md':
        return []

    # Skip index/metadata files
    if path.name.startswith('_') or path.name == '.obsidian':
        return []

    # Check modification time
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    if age_hours > modified_ago_hours:
        return []

    text = path.read_text(encoding='utf-8')

    # Determine category from path
    parts = path.relative_to(VAULT_PATH).parts
    category_map = {
        'papers': 'project',
        'experiments': 'general',
        'docs': 'general',
        'skills': 'general',
    }

    facts = []
    rel_path = str(path.relative_to(VAULT_PATH))
    note_name = path.stem

    # Extract tags from frontmatter
    tags = ''
    fm_match = re.search(r'^---\ntags:\s*\[(.+?)\]\n', text, re.MULTILINE)
    if fm_match:
        tags = fm_match.group(1)

    # Category from directory
    top_dir = parts[0] if parts else 'general'
    category = category_map.get(top_dir, 'general')

    # Find section headers
    sections = []
    for m in _SECTION_HEADER.finditer(text):
        sections.append(m.group(1))

    # Extract table rows as facts
    for m in _FACT_PATTERNS[0].finditer(text):
        key = m.group(1).strip()
        val = m.group(2).strip()
        if _RE_CJK.search(key) or _RE_CJK.search(val):
            content = f"[{note_name}] {key}: {val}"
            facts.append({'content': content[:400], 'category': category, 'tags': tags})

    # If no structured facts found, store the note title + first section
    if not facts and sections:
        first_section = sections[0] if sections else ''
        content = f"[{note_name}] {first_section}"
        facts.append({'content': content[:400], 'category': category, 'tags': tags})

    # Fallback: just the note title
    if not facts and _RE_CJK.search(note_name):
        content = f"[{note_name}] 在 {rel_path} 中"
        facts.append({'content': content[:400], 'category': category, 'tags': tags})

    return facts


def sync_to_memory(facts: list[dict], db_path: str) -> int:
    """Write extracted facts to the fact_store database."""
    if not facts:
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    added = 0
    for fact in facts:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO facts (content, category, tags) VALUES (?, ?, ?)",
                (fact['content'], fact['category'], fact.get('tags', '')),
            )
            if conn.total_changes > 0:
                added += 1
        except Exception:
            pass

    conn.commit()
    # Rebuild FTS index
    try:
        conn.execute("INSERT INTO facts_fts(facts_fts) VALUES('rebuild')")
        conn.commit()
    except Exception:
        pass
    conn.close()
    return added


def main():
    parser = argparse.ArgumentParser(description='Sync Obsidian → fact_store')
    parser.add_argument('--hours', type=float, default=24,
                        help='Scan window in hours (default: 24)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print what would be synced without writing')
    args = parser.parse_args()

    if not os.path.exists(VAULT_PATH):
        print(f"Vault not found: {VAULT_PATH}")
        sys.exit(1)

    # Walk the vault
    all_facts = []
    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fname in files:
            if not fname.endswith('.md'):
                continue
            filepath = os.path.join(root, fname)
            facts = extract_facts(filepath, args.hours)
            all_facts.extend(facts)

    if args.dry_run:
        print(f"Would sync {len(all_facts)} facts:")
        for f in all_facts:
            print(f"  [{f['category']}] {f['content'][:80]}")
        return

    added = 0
    if os.path.exists(MEMORY_DB):
        added = sync_to_memory(all_facts, MEMORY_DB)
        print(f"Synced {added} new facts to fact_store (from {len(all_facts)} candidates)")
    else:
        # Direct SQLite without the store wrapper
        conn = sqlite3.connect(MEMORY_DB)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'general',
                tags TEXT DEFAULT '',
                trust_score REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        added = sync_to_memory(all_facts, MEMORY_DB)
        print(f"Created memory DB, synced {added} facts")


if __name__ == '__main__':
    main()
