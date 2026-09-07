#!/usr/bin/env python3
"""
Synthos Evolution — DIAGNOSE script (v2.21)
Runs PROBE + BENCHMARK + DIAGNOSE in one pass and prints six-dimension scores.

Usage:
    cd /media/yakeworld/sda2/Synthos
    python3 skills/extended/meta/evolution/scripts/diagnose.py
"""

import os, json, re, subprocess, sys
import yaml

WORKDIR = os.environ.get('SYNTHOS_DIR', '/media/yakeworld/sda2/Synthos')
os.chdir(WORKDIR)

# ── PROBE ──────────────────────────────────────────────
total_skills = 0
yaml_valid_ct = 0
encoding_corrupt = 0
genes_section_ct = 0
gene_ids_ct = 0
gene_count_ok = 0
gene_dup_ct = 0
gene_section = r'^##\s+Genes'
# Gene ID uniqueness must count DEFINITION lines only ("- **[ID]** ..."),
# not prose references inside the Genes section (e.g. "与 DSH-008 组合").
# Cycle 266 fix: findall previously counted references as duplicate IDs
# (false positive: DSH-008 referenced in evolution/SKILL.md vs defined in dsh-self-evolution/SKILL.md).
gene_id = re.compile(r'^-\s*\*\*\[([A-Z]{2,4}-\d{3})\]\*\*', re.M)
seen_gene_ids = {}

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
                    fm = yaml.safe_load(parts[1])
                    if fm and isinstance(fm, dict):
                        yaml_valid_ct += 1
                except:
                    pass

            # Gene layer (v3 liveness inputs)
            gm = re.search(gene_section, content, re.M)
            if gm:
                genes_section_ct += 1
                rest = content[gm.start():]
                nxt = re.search(r'\n##\s+(?!Genes)', rest)
                seg = rest[:nxt.start()] if nxt else rest
                ids = list(dict.fromkeys(gene_id.findall(seg)))
                gene_ids_ct += len(ids)
                if 4 <= len(ids) <= 8:
                    gene_count_ok += 1
                for gid in ids:
                    seen_gene_ids[gid] = seen_gene_ids.get(gid, 0) + 1
            else:
                gene_ids_ct += 0

gene_dup_ct = sum(v - 1 for v in seen_gene_ids.values() if v > 1)

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
# Verification (验证清单) is the #1 quality metric: 40%
# Principles (思想密度): 20%
# Examples/Methods (可复现): 15%
# Deep/Thick content (实质性): 15%
# Rules/铁律 (约束): 5%
# Golden set (参考): 5%
# Note: verification is the bottleneck — all 191 skills should have verification
optimize = (
    verify_pct * 0.40 +
    principles_pct * 0.20 +
    example_pct * 0.15 +
    deep_pct * 0.15 +
    rules_pct * 0.05 +
    golden_pct * 0.05
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
            # Remove code blocks (multiline) and inline code
            clean = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            clean = re.sub(r'`[^`]*`', '', clean)
            ref_links = re.findall(r'\[.*?\]\(([^)]+)\)', clean)
            for ref in ref_links:
                # Skip external URLs and anchors (don't count in total)
                if ref.startswith('http') or ref.startswith('#') or ref.startswith('mailto'):
                    continue
                total_refs += 1
                # Check if relative path exists
                ref_path = os.path.join(os.path.dirname(path), ref)
                if not os.path.exists(ref_path):
                    coverage_errors += 1

coverage = 1.0 - (coverage_errors / total_refs) if total_refs else 1.0
coverage = min(1.0, max(0.0, coverage))

absorption = 1.0 - (total_dirty / total_skills) if total_skills else 0
constitutional = 1.0

# ── LIVENESS (v3, gene-layer vitality) ─────────────────
# 基因层活性: 进化最小单元 (Gene, CON v5.1 P7) 的存在/数量/唯一性
#   section_pct: 有 ## Genes 小节的技能占比
#   count_pct:   每技能 4-8 条 Gene (宪法标准) 达标占比
#   unique_pct:  基因 ID 全库唯一性 = 1 - 重复数/总基因数
# 当前权重: structural 0.20 / benchmark 0.20 / optimize 0.10 / coverage 0.10 /
#           absorption 0.10 / constitutional 0.20 / liveness 0.10
section_pct = genes_section_ct / total_skills if total_skills else 0
count_pct = gene_count_ok / total_skills if total_skills else 0
unique_pct = 1.0 - (gene_dup_ct / gene_ids_ct) if gene_ids_ct else 0.0
liveness = min(1.0, section_pct * 0.40 + count_pct * 0.30 + unique_pct * 0.30)

# ── BEHAVIOR (v4.1, 2026-09-07 reward-integrity) ──────
# 行为活性: 测"是否被执行"而非"文件是否完整" (锚定: 运行即证/取象通变)
#   activation_pct: pipeline_trace 中含 gene_activation 记录的比例 (行为留痕)
#   verify_pct:     trace 中原子 status=completed* 且产物可证实的比例
#                   (2026-09-07 评审实验1: "completed" 不再自动等于 "执行完成" —
#                    声称 output_file 但文件不存在 = 未证实, 不计入 verified;
#                    实测基线: 256 原子中 245 completed, 仅 5 个产物文件真实存在)
#                   (2026-09-07 评审三轮 补丁5 奖励单调性: 未声明产物的 completed
#                    同样不再默认计入 verified — 旧版 "无声明=无法证伪=计入" 使
#                    删除 output_file 字段反而提高 behavior (0.65→0.80 操纵路径)。
#                    未证实的 completed 计入 atom_unverified, 只作透明度输出, 不计分。)
#   lessons_pct:    失败轨迹沉淀 (10+ 条 = 1.0, 1-9 = 0.5, 0 = 0)
import glob
trace_files = glob.glob(os.path.join('outputs', '**', 'pipeline_trace*.json'), recursive=True)
act_ct = 0
atom_done = 0
atom_unverified = 0
atom_total = 0
for tf in trace_files:
    try:
        td = json.load(open(tf))
        if td.get('gene_activation'):
            act_ct += 1
        ats = td.get('atoms', {})
        if isinstance(ats, dict):
            base_dir = os.path.dirname(tf)
            for a in ats.values():
                if isinstance(a, dict):
                    atom_total += 1
                    if str(a.get('status', '')).startswith('completed'):
                        of = a.get('output_file')
                        if not of:
                            atom_unverified += 1  # 无产物声明 → 未证实, 不计入 (奖励单调性)
                        else:
                            p = of if os.path.isabs(of) else os.path.join(base_dir, of)
                            if os.path.exists(p):
                                atom_done += 1  # 产物存在 → 证实
                            else:
                                atom_unverified += 1  # 声称产物但不存在 → 未证实
    except Exception:
        pass
activation_pct = act_ct / len(trace_files) if trace_files else 0.0
verify_pct = atom_done / atom_total if atom_total else 0.0
lessons_ct = 0
_lf = os.path.join('outputs', 'evolution', 'lessons.jsonl')
if os.path.exists(_lf):
    with open(_lf) as _fh:
        lessons_ct = sum(1 for line in _fh if line.strip())
lessons_pct = 1.0 if lessons_ct >= 10 else (0.5 if lessons_ct >= 1 else 0.0)
behavior = min(1.0, activation_pct * 0.50 + verify_pct * 0.30 + lessons_pct * 0.20)

# v4 权重 (cycle 268): 8 维
# structural 0.18 / benchmark 0.18 / constitutional 0.18 / optimize 0.09 /
# coverage 0.09 / absorption 0.09 / liveness 0.09 / behavior 0.10
overall = (structural * 0.18 + benchmark * 0.18 + optimize * 0.09 +
           coverage * 0.09 + absorption * 0.09 + constitutional * 0.18 +
           liveness * 0.09 + behavior * 0.10)

# ── OUTPUT ─────────────────────────────────────────────
print(f"=== PROBE ===")
print(f"  Total SKILL.md: {total_skills}")
print(f"  YAML valid: {yaml_valid_ct}/{total_skills} ({yp*100:.1f}%)")
print(f"  Git tracked: {git_tracked}/{total_public}")
print(f"  Untracked: {untracked_public}")
print(f"  Dirty SKILL.md: {dirty_sk}")
print(f"  Total dirty: {total_dirty}")
print(f"  Encoding corrupt: {encoding_corrupt}")

print(f"\n=== LIVENESS (v3) ===")
print(f"  Genes section: {genes_section_ct}/{total_skills} ({section_pct*100:.1f}%)  x0.40 = {section_pct*0.40:.4f}")
print(f"  Count 4-8 ok:  {gene_count_ok}/{total_skills} ({count_pct*100:.1f}%)  x0.30 = {count_pct*0.30:.4f}")
print(f"  Unique IDs:    {gene_ids_ct - gene_dup_ct}/{gene_ids_ct} (dups={gene_dup_ct})  x0.30 = {unique_pct*0.30:.4f}")
print(f"  LIVENESS: {liveness:.4f}")

print(f"\n=== BEHAVIOR (v4) ===")
print(f"  gene_activation traces: {act_ct}/{len(trace_files)} ({activation_pct*100:.1f}%)  x0.50 = {activation_pct*0.50:.4f}")
print(f"  atoms completed:        {atom_done}/{atom_total} ({verify_pct*100:.1f}%)  x0.30 = {verify_pct*0.30:.4f}")
print(f"  atoms unverified:       {atom_unverified}/{atom_total} (completed 但产物未证实, 不计分 — 奖励单调性, 评审三轮)")
print(f"  lessons:                {lessons_ct}  x0.20 = {lessons_pct*0.20:.4f}")
print(f"  BEHAVIOR: {behavior:.4f}")

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
    'liveness': liveness,
    'behavior': behavior,
}
for k, v in sorted(dims.items(), key=lambda x: x[1]):
    print(f"  {k:20s}: {v:.4f}")

lowest = min(dims, key=dims.get)
print(f"\n  LOWEST: {lowest} ({dims[lowest]:.4f})")

print(f"\n=== OVERALL (v4, 8-dim) ===")
print(f"  structural({structural:.4f})   x0.18 = {structural*0.18:.4f}")
print(f"  benchmark({benchmark:.4f})    x0.18 = {benchmark*0.18:.4f}")
print(f"  optimize({optimize:.4f})     x0.09 = {optimize*0.09:.4f}")
print(f"  coverage({coverage:.4f})     x0.09 = {coverage*0.09:.4f}")
print(f"  absorption({absorption:.4f})  x0.09 = {absorption*0.09:.4f}")
print(f"  constitutional({constitutional:.4f}) x0.18 = {constitutional*0.18:.4f}")
print(f"  liveness({liveness:.4f})     x0.09 = {liveness*0.09:.4f}")
print(f"  behavior({behavior:.4f})     x0.10 = {behavior*0.10:.4f}")
print(f"  ─────────────────────────────────────────")
print(f"  OVERALL: {overall:.4f}")

# State comparison
# 2026-09-06 修复: state 变量此前从未加载, 本块一直在 except: pass 中静默失败
# (自检从未真正运行). 现显式加载; 仍保留容错 (state 文件缺失/损坏时跳过).
try:
    import json as _json, os as _os
    with open(_os.path.join('evolution-state.json')) as _f:
        state = _json.load(_f)
    state_score = state.get('score', state.get('overall_score', 0))
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
