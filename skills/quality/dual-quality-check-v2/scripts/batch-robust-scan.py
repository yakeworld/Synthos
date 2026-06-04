#!/usr/bin/env python3
"""
batch-robust-scan.py — 全库D10a批量扫描 & 结果分类

对 outputs/papers/ 下每篇论文运行 robust-d10a-scanner，聚合结果，
按已知假阳性模式自动分类，输出仅含真实问题的简洁报告。

用法:
  python3 scripts/batch-robust-scan.py [--dir /path/to/papers] [--verbose] [--fix]

选项:
  --dir      论文目录 (默认: 自动搜索 Synthos outputs/papers/)
  --verbose  输出每篇论文的详细扫描结果
  --fix      对可自动修复的问题执行修复 (P0孤儿引用警告 — 优先当前手动处理)

输出:
  stdout 格式:
    [分类标签] 论文名: D8=N D10a=N% (扫描: D8=N D10a=N%)
    分类标签: CLEAN / ZOMBIE / ORPHAN_P0 / SKELETON / SUBFILE / BENCHMARK

  分类规则:
    CLEAN       — D8>=30 AND D10a>=100
    ZOMBIE      — D10a<100 AND orphans=0 AND zombies>0 (有bib无cite)
    ORPHAN_P0   — D10a<100 AND orphans>0 (有cite无bib — 零容忍)
    SKELETON    — D8>0 AND D10a<100 AND tex行数<300 (骨架论文)
    SUBFILE     — 主tex有\\input{}无\\cite{} (子文件结构)
    BENCHMARK   — D8<30 AND D10a=100 (小引用量论文, 如crispdm-heart)
    NO_TEX      — 找不到主tex文件
"""

import os, re, sys, subprocess, argparse

def find_papers_dir():
    candidates = [
        "/media/yakeworld/sda2/Synthos/outputs/papers",
        os.path.expanduser("~/Synthos/outputs/papers"),
        "outputs/papers",
    ]
    for c in candidates:
        if os.path.isdir(c) and any(
            os.path.isdir(os.path.join(c, d)) and not d.startswith("_")
            for d in os.listdir(c)
        ):
            return c
    return None

def find_tex_file(paper_dir):
    """找到主tex文件 (优先级: improved/v4 > paper > main > article)"""
    candidates = []
    for subdir in ["", "01-manuscript", "02-submission", "paper"]:
        sd = os.path.join(paper_dir, subdir) if subdir else paper_dir
        if not os.path.isdir(sd):
            continue
        for f in os.listdir(sd):
            fp = os.path.join(sd, f)
            if not (f.endswith(".tex") and os.path.isfile(fp)):
                continue
            if f.startswith("fig_") and os.path.getsize(fp) < 5000:
                continue
            score = 0
            if "improved" in f or "v4" in f or "v5" in f:
                score = 10
            elif f == "paper-synthos.tex":
                score = 9
            elif f == "paper.tex":
                score = 5
            elif f == "main.tex":
                score = 4
            elif f in ("article.tex", "synthos-paper.tex", "scf-paper.tex"):
                score = 3
            else:
                score = 1
            candidates.append((score, fp))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None

def classify_paper(paper_name, d8, d10a, tex_path, robust_out):
    """根据已知假阳性模式分类"""
    # 1. 子文件结构检测
    if tex_path and os.path.isfile(tex_path):
        tex = open(tex_path).read()
        has_input = "\\input{" in tex
        tex_lines = len(tex.split("\n"))
        tex_cites_in_main = len(re.findall(r"\\cite[tp]?\s*\{", tex))
    else:
        has_input = False
        tex_lines = 0
        tex_cites_in_main = 0

    # 2. 分类逻辑
    if d10a >= 100 and d8 >= 30:
        return "CLEAN"
    if d10a >= 100 and d8 < 30:
        return "BENCHMARK"
    if d10a < 100:
        # 检查是否有孤儿引用
        if "ORPHAN" in robust_out or "orphan" in robust_out:
            return "ORPHAN_P0"
        if has_input and tex_cites_in_main == 0:
            return "SUBFILE"
        if tex_lines < 300:
            return "SKELETON"
        return "ZOMBIE"
    return "CLEAN"

def main():
    parser = argparse.ArgumentParser(description="Batch D10a scan with classification")
    parser.add_argument("--dir", help="Papers directory")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-fix")
    args = parser.parse_args()

    papers_dir = args.dir or find_papers_dir()
    if not papers_dir:
        print("ERROR: Cannot find papers directory. Use --dir")
        sys.exit(1)

    # Find robust scanner
    scanner = None
    for p in [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "references", "robust-d10a-scanner-2026-06-01.py"),
        "/media/yakeworld/sda2/Synthos/skills/quality/dual-quality-check-v2/references/robust-d10a-scanner-2026-06-01.py",
    ]:
        if os.path.isfile(p):
            scanner = p
            break
    if not scanner:
        print("WARNING: robust-d10a-scanner not found, using inline scan")
    else:
        print(f"Using scanner: {scanner}", file=sys.stderr)

    papers = sorted(os.listdir(papers_dir))
    categories = {"CLEAN": 0, "ZOMBIE": 0, "ORPHAN_P0": 0,
                  "SKELETON": 0, "SUBFILE": 0, "BENCHMARK": 0, "NO_TEX": 0}
    results = []

    for paper in papers:
        dp = os.path.join(papers_dir, paper)
        if not os.path.isdir(dp) or paper.startswith("_") or paper in ["lit-reviews", "hold"]:
            continue

        tex_path = find_tex_file(dp)
        if not tex_path:
            categories["NO_TEX"] += 1
            print(f"[NO_TEX]   {paper}: —")
            continue

        if scanner and os.path.isfile(scanner):
            try:
                r = subprocess.run(["python3", scanner, tex_path],
                                   capture_output=True, text=True, timeout=30)
                robust_out = r.stdout.strip()
            except subprocess.TimeoutExpired:
                robust_out = f"D8=0 D10a=0% (timeout)"
        else:
            # inline fallback scan
            robust_out = ""
            try:
                tex = open(tex_path).read()
                lines = [l for l in tex.split("\n") if not l.strip().startswith("%")]
                active = "\n".join(lines)
                has_thebib = "\\begin{thebibliography}" in active
                has_bib = "\\bibliography{" in active
                cites = set()
                for m in re.finditer(r"\\cite[tp]?\s*\{([^}]+)\}", active):
                    for k in m.group(1).split(","):
                        cites.add(k.strip())
                if has_thebib and not has_bib:
                    bibitems = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", active))
                    d8 = len(bibitems)
                    matched = sum(1 for k in cites if k in bibitems)
                    d10a = matched / d8 * 100 if d8 else 0
                    robust_out = f"D8={d8} D10a={d10a:.0f}%"
                else:
                    # find bib file
                    bib_path = None
                    for bname in ["06-references/references.bib", "references.bib", "refs.bib"]:
                        bp = os.path.join(dp, bname)
                        if os.path.isfile(bp):
                            bib_path = bp
                            break
                    if bib_path:
                        bib = open(bib_path).read()
                        bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
                        d8 = len(bib_keys)
                        matched = sum(1 for k in cites if k in bib_keys)
                        d10a = matched / d8 * 100 if d8 else 0
                        robust_out = f"D8={d8} D10a={d10a:.0f}%"
                    else:
                        robust_out = "D8=0 D10a=0% (no bib)"
            except Exception as e:
                robust_out = f"D8=0 D10a=0% (error: {e})"

        # Parse result
        m_d8 = re.search(r"D8=\\s*(\\d+)", robust_out)
        m_d10 = re.search(r"D10a=([0-9.]+)", robust_out)
        d8 = int(m_d8.group(1)) if m_d8 else 0
        d10a = float(m_d10.group(1)) if m_d10 else 0

        # BBL/AUX fallback: if scanning shows D10a<100 or D8==0,
        # try compiled .bbl and .aux files (for \\input{} subfile structure)
        if d10a < 100 or d8 == 0:
            for root, dirs, files in os.walk(dp):
                for f in files:
                    if f.endswith('.aux') and os.path.getsize(os.path.join(root, f)) > 50:
                        with open(os.path.join(root, f)) as fh:
                            aux = fh.read()
                        aux_cites = set()
                        for m in re.finditer(r'\\citation\\{([^}]+)\\}', aux):
                            for k in m.group(1).split(','):
                                aux_cites.add(k.strip())
                        if aux_cites:
                            bbl_path = os.path.join(os.path.dirname(os.path.join(root, f)),
                                                    f.replace('.aux', '.bbl'))
                            if os.path.isfile(bbl_path):
                                with open(bbl_path) as fh:
                                    bbl = fh.read()
                                bbl_keys = set(re.findall(r'\\bibitem\\{([^}]+)\\}', bbl))
                                if bbl_keys:
                                    matched = len(aux_cites & bbl_keys)
                                    d8 = len(bbl_keys)
                                    d10a = matched / d8 * 100 if d8 else 0
                                    robust_out = f"D8={d8} D10a={d10a:.0f}% (from .bbl/.aux)"
                        break
                if d8 > 0:
                    break

        category = classify_paper(paper, d8, d10a, tex_path, robust_out)
        categories[category] = categories.get(category, 0) + 1
        results.append((category, paper, d8, d10a, robust_out))

        if args.verbose or category not in ("CLEAN",):
            print(f"[{category:10s}] {paper}: D8={d8} D10a={d10a:.0f}%")
            if args.verbose and category == "CLEAN":
                print(f"  -> scan: {robust_out}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    issues = [(c, n) for c, n in categories.items()
              if c not in ("CLEAN", "BENCHMARK") and n > 0]
    if issues:
        print(f"Papers needing attention ({sum(n for _, n in issues)}):")
        for cat, n in sorted(issues, key=lambda x: -x[1]):
            print(f"  {cat}: {n}")
    else:
        print("All papers clean.")
    print(f"\nTotal scanned: {sum(categories.values())}")
    print(f"  CLEAN:    {categories.get('CLEAN', 0)}")
    print(f"  BENCHMARK: {categories.get('BENCHMARK', 0)}")
    print(f"  SUBFILE:  {categories.get('SUBFILE', 0)}  (假阳性 — 子文件结构)")
    print(f"  SKELETON: {categories.get('SKELETON', 0)}  (假阳性 — 骨架论文)")
    print(f"  ZOMBIE:   {categories.get('ZOMBIE', 0)}  (真实问题 — 僵尸引用)")
    print(f"  ORPHAN:   {categories.get('ORPHAN_P0', 0)}  (真实问题 — 孤儿引用 P0)")
    print(f"  NO_TEX:   {categories.get('NO_TEX', 0)}")

    # Fix mode
    if args.fix and categories.get("ZOMBIE", 0) > 0:
        print("\n AUTO-FIX NOT IMPLEMENTED — zombie activation requires human judgment")
        print(" Run: python3 scripts/thebibliography_zombie_cleanup.py paper.tex --dry-run")

    return 0 if categories.get("ORPHAN_P0", 0) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
