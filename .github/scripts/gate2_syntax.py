#!/usr/bin/env python3
"""Gate 2: Validate syntax of changed files (from git diff or args)"""
import os, sys, json, yaml, subprocess

# Get changed files from git diff
r = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                   capture_output=True, text=True, cwd=os.getcwd())
changed = [f.strip() for f in r.stdout.strip().split('\n') if f.strip()]

if not changed:
    # Fall back to checking PR common paths
    changed = sys.argv[1:] if len(sys.argv) > 1 else []

errors = 0
validators = {
    '.yaml': lambda p: yaml.safe_load(open(p)),
    '.yml': lambda p: yaml.safe_load(open(p)),
    '.json': lambda p: json.load(open(p)),
    '.py': lambda p: subprocess.run(['python3', '-m', 'py_compile', p],
                                     capture_output=True).returncode == 0,
}

for f in changed:
    ext = os.path.splitext(f)[1]
    if ext in validators and os.path.exists(f):
        try:
            validators[ext](f)
            print(f"  ✅ {f}")
        except Exception as e:
            print(f"  ❌ {f}: {e}")
            errors += 1

sys.exit(errors)
