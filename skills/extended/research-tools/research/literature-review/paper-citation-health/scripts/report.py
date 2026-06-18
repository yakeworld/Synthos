#!/usr/bin/env python3
"""Generate clean formatted report from the scan JSON output.

Usage: python3 report.py
Reads stdout from d8-d10a-scan-v2.py, parses table rows, and outputs
a categorized report with healthy/problem paper breakdowns.
"""
import subprocess, sys

result = subprocess.run(
    [sys.executable, "/home/yakeworld/.hermes/skills/research/paper-citation-health/scripts/d8-d10a-scan-v2.py"],
    capture_output=True, text=True
)

lines = result.stdout.strip().split('\n')

def d10a_val(s):
    try:
        return int(s.replace('%',''))
    except:
        return 0

rows = []
for line in lines:
    if '📊' in line or 'D8 | D10a' in line:
        continue
    if not line.strip():
        continue
    if not line.strip().startswith('|'):
        break
    if 'D8 | D10a' in line or ':---' in line:
        continue
    parts = [p.strip() for p in line.strip('|').split('|')]
    if len(parts) < 6:
        continue
    try:
        d8 = int(parts[1])
        int(parts[3])
        int(parts[4])
    except ValueError:
        continue
    name = parts[0]
    if not name or name.startswith(':'):
        continue
    rows.append((name, d8, d10a_val(parts[2]), int(parts[3]), int(parts[4]), parts[5]))

# Remove "." root directory
rows = [r for r in rows if r[0] != '.']

total = len(rows)
problems = [r for r in rows if r[1] < 30 or r[2] < 100]
healthy = total - len(problems)

no_bib = [r for r in problems if r[1] == 0 and r[2] == 0]
partial_orphan = [r for r in problems if r[1] > 0 and r[2] < 100]
low_d8_full_match = [r for r in problems if r[1] > 0 and r[1] < 30 and r[2] == 100]
missing_bbl = [r for r in problems if r[5] == '❌']

total_orphans = sum(r[3] for r in rows)
total_zombies = sum(r[4] for r in rows)

max_name_width = 45

print("📊 论文全库扫描报告")
print()
print(f"| {'论文':<{max_name_width}} | D8 | D10a | 孤儿 | 僵尸 | 编译 |")
print(f"|{'-'*max_name_width}-|:--:|:----:|:----:|:----:|:----:|")
for n, d8, d10a, orph, zomb, comp in rows:
    display = n if len(n) <= max_name_width else n[:max_name_width-3] + '...'
    print(f"| {display} | {d8} | {d10a}% | {orph} | {zomb} | {comp} |")

print()
print(f"总计: {total}篇, 健康: {healthy}篇, 问题: {len(problems)}篇")
print(f"总引用数: {sum(r[1]+r[2] for r in rows)}, 总孤儿: {total_orphans}, 总僵尸: {total_zombies}")

if problems:
    print()
    print("问题论文 (D10a<100% 或 D8<30):")
    print()
    
    if no_bib:
        print(f"🔴 无BIB文件 ({len(no_bib)}篇):")
        by_orphans = sorted(no_bib, key=lambda r: r[3], reverse=True)
        for r in by_orphans:
            display = r[0] if len(r[0]) <= 45 else r[0][:42] + '...'
            cite_count = r[3]  # all citations are orphans
            print(f"  - {display}: D8=0, D10a=0%, 引用={cite_count}, 孤儿={r[3]}, 编译={'✅' if r[5]=='✅' else '❌'}")
        print()

    if partial_orphan:
        print(f"🟡 D10a<100% ({len(partial_orphan)}篇):")
        by_d10a = sorted(partial_orphan, key=lambda r: r[2])
        for r in by_orphans:
            display = r[0] if len(r[0]) <= 45 else r[0][:42] + '...'
            print(f"  - {display}: D8={r[1]}, D10a={r[2]}%, 孤儿={r[3]}, 僵尸={r[4]}, 编译={'✅' if r[5]=='✅' else '❌'}")
        print()

    if low_d8_full_match:
        print(f"🟡 D8<30 但D10a=100% ({len(low_d8_full_match)}篇):")
        for r in low_d8_full_match:
            display = r[0] if len(r[0]) <= 45 else r[0][:42] + '...'
            print(f"  - {display}: D8={r[1]}, D10a={r[2]}%, 引用=0, 僵尸={r[4]}, 编译={'✅' if r[5]=='✅' else '❌'}")
        print()

    print(f"⚠️  未编译论文: {len(missing_bbl)}篇 / {total}篇 ({100*len(missing_bbl)//total}%)")

print()
print("📋 关键发现:")
print(f"  · 总论文数: {total}")
print(f"  · 完全健康 (D10a=100%, D8>=30): {sum(1 for r in rows if r[1]>=30 and r[2]==100)}")
print(f"  · 无BIB文件: {len(no_bib)}")
print(f"  · 总孤儿引用数: {total_orphans}")
print(f"  · 总僵尸引用数: {total_zombies}")
print(f"  · 已编译(.bbl): {sum(1 for r in rows if r[5]=='✅')}")
print(f"  · 未编译: {sum(1 for r in rows if r[5]=='❌')}")