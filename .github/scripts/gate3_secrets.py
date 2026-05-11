#!/usr/bin/env python3
"""Gate 3: Scan changed files for hardcoded secrets"""
import os, re, sys, subprocess

# Get changed files
r = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                   capture_output=True, text=True, cwd=os.getcwd())
changed = [f.strip() for f in r.stdout.strip().split('\n') if f.strip()]

patterns = [
    ("Generic 20+ char token", r'["'"'"'][A-Za-z0-9_-]{20,}["'"'"']'),
    ("OpenAI key", r'sk-[A-Za-z0-9_-]{20,}'),
    ("GitHub PAT", r'ghp_[A-Za-z0-9_-]{36,}'),
    ("Private key", r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
    ("AWS key", r'AKIA[A-Z0-9]{16}'),
    ("S2 key", r's2k-[A-Za-z0-9_-]{20,}'),
]

exclude = ['VERIFICATION_GATES.md', 'AGENTS_CONTRIBUTING.md', '.github/']
found = []

for f in changed:
    if any(e in f for e in exclude):
        continue
    if not os.path.exists(f):
        continue
    try:
        with open(f, 'r', errors='ignore') as fh:
            content = fh.read()
    except:
        continue

    for name, pat in patterns:
        for m in re.finditer(pat, content):
            line = content[:m.start()].count('\n') + 1
            found.append((f, line, name, m.group()[:30]))

if found:
    for path, line, name, snippet in found:
        print(f"  ❌ {path}:{line} ({name}: {snippet})")
    sys.exit(1)
else:
    print("✅ No secrets detected")
