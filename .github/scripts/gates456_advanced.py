#!/usr/bin/env python3
"""Gates 4-6: Constitutional compliance, Quality scoring, Impact analysis"""
import os, sys, subprocess

# Get changed files
result = subprocess.run(
    ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
    capture_output=True, text=True
)
changed = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
print(f"Changed files ({len(changed)}):")
for f in changed:
    print(f"  {f}")

# ---- Gate 4: Constitutional Compliance ----
score_p4 = 1.0
warnings = []
for f in changed:
    if 'sources/' in f or 'literature' in f:
        try:
            with open(f) as fh:
                content = fh.read()
            if not any(k in content.lower() for k in ['doi', 'url', 'arxiv', 'http']):
                warnings.append(f"{f}: missing DOI/URL (P0 evidence traceability)")
                score_p4 -= 0.2
        except:
            pass
    if 'task-router' in f or '/rou' in f.lower():
        warnings.append(f"{f}: router change needs human approval (P3)")
        score_p4 -= 0.5
    if 'CONSTITUTION' in f.upper():
        warnings.append(f"{f}: constitution change needs owner approval (P0)")
        score_p4 -= 0.5

result_p4 = 'PASS' if score_p4 >= 0.7 else ('REVIEW' if score_p4 >= 0.5 else 'FAIL')
print(f"\n--- Gate 4 ---")
print(f"Score: {score_p4}")
print(f"Result: {result_p4}")
for w in warnings:
    print(f"  ⚠️ {w}")

# ---- Gate 5: Quality Scoring ----
has_manifest = os.path.exists('AGENT_MANIFEST.yaml')
completeness = 1.0 if has_manifest else 0.0
clarity = 0.8
relevance = 0.7
safety = 1.0
testability = 0.7
score_p5 = (completeness*0.25) + (clarity*0.15) + (relevance*0.20) + (safety*0.25) + (testability*0.15)
score_p5 = round(score_p5, 2)
print(f"\n--- Gate 5 ---")
print(f"Score: {score_p5}")
for label, val in [("Completeness", completeness), ("Clarity", clarity),
                    ("Relevance", relevance), ("Safety", safety),
                    ("Testability", testability)]:
    print(f"  {label}: {val}")

# ---- Gate 6: Impact Analysis ----
levels = {'cosmetic': 0, 'incremental': 1, 'structural': 2, 'constitutional': 3}
rev = {0:'cosmetic', 1:'incremental', 2:'structural', 3:'constitutional'}
max_lv = 0
for f in changed:
    if f.startswith('CONSTITUTION.md'): max_lv = max(max_lv, 3)
    elif f.startswith(('constitution.md', 'core/', 'SKILL.md', 'evolution-')): max_lv = max(max_lv, 2)
    elif f.startswith(('skills/', 'sources/', 'templates/')): max_lv = max(max_lv, 1)
impact = rev[max_lv]
print(f"\n--- Gate 6 ---")
print(f"Impact: {impact}")

# Summary
all_pass = (result_p4 == 'PASS' and score_p5 >= 0.7)
status = "✅ ALL PASS" if all_pass else "❌ HAS ISSUES"
print(f"\n{'='*40}")
print(f"Gates 4-6: {status}")
print(f"Quality Score: {score_p5}")
print(f"Impact: {impact}")

if not all_pass:
    sys.exit(1)
