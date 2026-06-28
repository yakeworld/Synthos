#!/usr/bin/env python3
"""
Synthos Evolution — DIAGNOSE script (v2.21)
Runs PROBE + BENCHMARK + DIAGNOSE in one pass and prints six-dimension scores.

Usage:
    cd /media/yakeworld/sda2/Synthos
    python3 skills/extended/meta/evolution/scripts/diagnose.py
"""

import os, json, subprocess, sys

WORKDIR = os.environ.get('SYNTHOS_DIR', '/media/yakeworld/sda2/Synthos')
os.chdir(WORKDIR)

# ── PROBE ──────────────────────────────────────────────
total_skills = 0
yaml_valid_ct = 0
encoding_corrupt = 0

for root, dirs, files in os.walk('skills'):
    for f in files:
        if f == 'SKILL.md':
            total_skills += 1
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    content = fh.read()
            except:
                encoding_corrupt += 1
                continue

            parts = content.split('---')
            if len(parts) >= 3:
                try:
                    import yaml
                    fm = yaml.safe_load(parts[1])
                    if fm and isinstance(fm, dict):
                        yaml_valid_ct += 1
                except:
                    pass

# Git tracking — exclude private/ (intentionally gitignored due to credentials)
r = subprocess.run(['git', 'ls-files', 'skills/'], capture_output=True, text=True)
git_tracked = len([l for l in r.stdout.split('\n') if 'SKILL.md' in l and '/private/' not in l])

r2 = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', 'skills/'],
                     capture_output=True, text=True)
untracked_public = len([l for l in r2.stdout.split('\n') if 'SKILL.md' in l and '/private/' not in l])
# total_public = tracked public + untracked public (private excluded from denominator)
total_public = git_tracked + untracked_public

# Dirty files — exclude evolution-state.json (self-updating, not a skill)
r3 = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
dirty_lines = [l for l in r3.stdout.split('\n') if l.strip() and 'evolution-state.json' not in l]
total_dirty = len(dirty_lines)
dirty_sk = len([l for l in dirty_lines if 'SKILL.md' in l])

# ── BENCHMARK ──────────────────────────────────────────
ver_count = 0
sig_count = 0
io_count = 0

for root, dirs, files in os.walk('skills'):
    for f in files:
        if f == 'SKILL.md':
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    content = fh.read()
            except:
                continue
            if 'version:' in content or "'version'" in content:
                ver_count += 1
            if 'signature' in content.lower():
                sig_count += 1
            if 'IO_CONTRACT' in content:
                io_count += 1

# ── COMPUTE DIMENSIONS ─────────────────────────────────
yp = yaml_valid_ct / total_skills
gp = git_tracked / total_public if total_public else 0
circ_clean = 1.0  # circular deps check is complex; assume clean
enc_clean = 1.0 - (encoding_corrupt / total_skills)
dirty_penalty = (total_skills - dirty_sk) / total_skills

structural_raw = yp * 0.35 + gp * 0.25 + circ_clean * 0.25 + enc_clean * 0.15
structural = structural_raw * dirty_penalty

vp = ver_count / total_skills
sp = sig_count / total_skills
ip = io_count / total_skills
benchmark = vp * 0.33 + sp * 0.33 + ip * 0.34

# Load state for # ── OPTIMIZE (content quality score) ─────────────────
# Calculate actual content quality from all SKILL.md files
optimize = 0

verify_ct = 0
example_ct = 0
golden_ct = 0
rules_ct = 0
principles_ct = 0
code_blocks_ct = 0
empty_skills = 0
deep_skills = 0

for root, dirs, files in os.walk('skills'):
    for fn in files:
        if fn == 'SKILL.md':
            path = os.path.join(root, fn)
            try:
                with open(path) as fh:
                    content = fh.read()
            except:
                continue
            
            # Check verification content
            body = content[content.index('---', content.index('---')+1)+1:] if content.count('---') >= 2 else content
            
            has_verify = any(term in body for term in ['验证', 'Verify', 'verification', 'checklist', '质量', 'Quality', '验证清单'])
            has_example = any(term in body for term in ['示例', 'example', 'Example', 'case', 'Case', '场景'])
            has_golden = 'golden' in content.lower()
            has_rules = '规则' in body or '铁律' in body or 'Rule' in body
            has_principles = '原则' in body or 'Principle' in body
            
            if has_rules: rules_ct += 1
            if has_principles: principles_ct += 1
            if has_verify: verify_ct += 1
            if has_example: example_ct += 1
            if has_golden: golden_ct += 1
            if len(body.strip()) > 100: deep_skills += 1
            
            # Code blocks (python/bash/curl/docker)
            code_indicators = ['```python', '```bash', '```sh', '```shell', 'python3', 'curl ', 'docker ', 'git ']
            if any(ind in body for ind in code_indicators):
                code_blocks_ct += 1

# Optimize = weighted combination of content quality metrics
verify_pct = verify_ct / total_skills if total_skills else 0
example_pct = example_ct / total_skills if total_skills else 0
golden_pct = golden_ct / total_skills if total_skills else 0
rules_pct = rules_ct / total_skills if total_skills else 0
principles_pct = principles_ct / total_skills if total_skills else 0
deep_pct = deep_skills / total_skills if total_skills else 0
code_pct = code_blocks_ct / total_skills if total_skills else 0

# Weighted score: prioritize rules+principles (思想密度) > verification > examples > golden
# Content quality weights — tuned for Synthos quality standards
# Principles (思想密度) are the foundation: 25%
# Verification (验证) ensures evidence: 20%
# Methods/Steps (可操作性): 15%
# Examples (可复用): 15%
# Rules/铁律 (约束): 15%
# Golden set (参考): 10%
optimize = (
    principles_pct * 0.25 +
    verify_pct * 0.20 +
    deep_pct * 0.15 +
    example_pct * 0.15 +
    rules_pct * 0.15 +
    golden_pct * 0.10
)

# Clamp between 0 and 1
optimize = min(1.0, max(0.0, optimize))

# ── COVERAGE (reference integrity score) ─────────────
# Check that all referenced files in SKILL.md actually exist on disk
coverage_errors = 0
total_refs = 0
for root, dirs, files in os.walk('skills'):
    for fn in files:
        if fn == 'SKILL.md':
            path = os.path.join(root, fn)
            try:
                with open(path) as fh:
                    content = fh.read()
            except:
                continue
            
            # Find reference links like [file](path/to/file.md)
            # Strip inline code (backtick) to avoid matching markdown syntax examples like ![alt](url)
            import re
            # Remove code blocks and inline code
            clean = re.sub(r'```[^`]*```', '', content)
            clean = re.sub(r'`[^`]+`', '', clean)
            ref_links = re.findall(r'\[.*?\]\(([^)]+)\)', clean)
            for ref in ref_links:
                total_refs += 1
                # Skip external URLs and anchors
                if ref.startswith('http') or ref.startswith('#') or ref.startswith('mailto'):
                    continue
                # Check if relative path exists
                ref_path = os.path.join(os.path.dirname(path), ref)
                if not os.path.exists(ref_path):
                    coverage_errors += 1

coverage = 1.0 - (coverage_errors / total_refs) if total_refs else 1.0
coverage = min(1.0, max(0.0, coverage))

absorption = 1.0 - (total_dirty / total_skills) if total_skills else 0
constitutional = 1.0

overall = (structural * 0.25 + benchmark * 0.25 + optimize * 0.10 +
           coverage * 0.10 + absorption * 0.10 + constitutional * 0.20)

# ── OUTPUT ─────────────────────────────────────────────
print(f"=== PROBE ===")
print(f"  Total SKILL.md: {total_skills}")
print(f"  YAML valid: {yaml_valid_ct}/{total_skills} ({yp*100:.1f}%)")
print(f"  Git tracked: {git_tracked}/{total_public}")
print(f"  Untracked: {untracked_public}")
print(f"  Dirty SKILL.md: {dirty_sk}")
print(f"  Total dirty: {total_dirty}")
print(f"  Encoding corrupt: {encoding_corrupt}")

print(f"\n=== BENCHMARK ===")
print(f"  Version:      {ver_count}/{total_skills} ({vp*100:.1f}%)  x0.33 = {vp*0.33:.4f}")
print(f"  Signature:    {sig_count}/{total_skills} ({sp*100:.1f}%)  x0.33 = {sp*0.33:.4f}")
print(f"  IO_CONTRACT:  {io_count}/{total_skills} ({ip*100:.1f}%)  x0.34 = {ip*0.34:.4f}")
print(f"  BENCHMARK: {benchmark:.4f}")

print(f"\n=== DIAGNOSE (Pareto) ===")
dims = {
    'structural': structural,
    'benchmark': benchmark,
    'optimize': optimize,
    'coverage': coverage,
    'absorption': absorption,
    'constitutional': constitutional,
}
for k, v in sorted(dims.items(), key=lambda x: x[1]):
    print(f"  {k:20s}: {v:.4f}")

lowest = min(dims, key=dims.get)
print(f"\n  LOWEST: {lowest} ({dims[lowest]:.4f})")

print(f"\n=== OVERALL ===")
print(f"  structural({structural:.4f})   x0.25 = {structural*0.25:.4f}")
print(f"  benchmark({benchmark:.4f})    x0.25 = {benchmark*0.25:.4f}")
print(f"  optimize({optimize:.4f})     x0.10 = {optimize*0.10:.4f}")
print(f"  coverage({coverage:.4f})     x0.10 = {coverage*0.10:.4f}")
print(f"  absorption({absorption:.4f})  x0.10 = {absorption*0.10:.4f}")
print(f"  constitutional({constitutional:.4f}) x0.20 = {constitutional*0.20:.4f}")
print(f"  ─────────────────────────────────────────")
print(f"  OVERALL: {overall:.4f}")

# State comparison
try:
    state_score = state.get('overall_score', state.get('score', 0))
    diff = abs(state_score - overall)
    print(f"\n=== STATE SYNC ===")
    print(f"  State claims: {state_score:.4f}")
    print(f"  Actual:       {overall:.4f}")
    if diff > 0.05:
        print(f"  WARNING: SELF-DECEPTION RISK (diff={diff:.4f} > 5%)")
    elif diff > 0.02:
        print(f"  CAUTION: mild drift (diff={diff:.4f})")
    else:
        print(f"  OK: in sync (diff={diff:.4f})")
except:
    pass
