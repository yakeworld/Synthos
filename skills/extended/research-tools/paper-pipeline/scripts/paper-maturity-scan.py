#!/usr/bin/env python3
"""
Paper Maturity Scan — 扫描论文库中所有论文的成熟度，按成熟度排序。

成熟度评分维度：
- 引用数 ≥50: 15分, ≥30: 10分
- D10a ≥95%: 15分, ≥80%: 10分, ≥60%: 5分
- 编译PDF >500KB: 15分
- quality_score ≥0.85: 15分, ≥0.70: 10分
- quality_check.md: 10分
- index.md: 5分
- Graphical Abstract: 5分
- Figure ≥3: 10分
- 引用数 ≥30: 10分

输出：按总分排序，分数越高越成熟。

使用：cd /media/yakeworld/sda2/Synthos/outputs/papers/ && python3 ../../skills/paper-pipeline/scripts/paper-maturity-scan.py
"""
import os
import re
import json

PAPERS_DIR = os.environ.get('PAPERS_DIR', '/media/yakeworld/sda2/Synthos/outputs/papers/')

def scan_papers(papers_dir):
    """扫描所有论文目录，返回成熟度评分列表。"""
    results = []
    for name in sorted(os.listdir(papers_dir)):
        path = os.path.join(papers_dir, name)
        if not os.path.isdir(path) or name.startswith('_') or name.startswith('.'):
            continue
        mdir = os.path.join(path, '01-manuscript')
        if not os.path.isdir(mdir):
            continue
        tex_files = [f for f in os.listdir(mdir) if f.endswith('.tex') and 'template' not in f and 'cover' not in f and 'letter' not in f]
        if not tex_files:
            continue
        for tf in tex_files:
            with open(os.path.join(mdir, tf)) as f:
                content = f.read()
            # Unique cite keys for D10a
            all_keys = set()
            for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', content):
                for k in m.group(1).split(','):
                    k = k.strip()
                    if k and len(k) > 2 and k not in ('label', 'lamport94', 'citep', 'cite'):
                        all_keys.add(k)
            total_cites = len(re.findall(r'\\cite', content))
            if total_cites < 10:
                continue
            # Bib entries
            bib_count = 0
            seen_keys = set()
            for bp in [path, os.path.join(path, '06-references')]:
                if not os.path.isdir(bp):
                    continue
                for ff in os.listdir(bp):
                    if ff.endswith('.bib'):
                        try:
                            with open(os.path.join(bp, ff)) as fh:
                                bcontent = fh.read()
                            for bm in re.finditer(r'@\w+\{([^,}]+),', bcontent):
                                key = bm.group(1).strip()
                                if key not in seen_keys:
                                    seen_keys.add(key)
                                    bib_count += 1
                        except:
                            pass
            # D10a: unique cite keys intersected with bib keys
            d10a = len(all_keys.intersection(seen_keys)) / max(bib_count, 1) * 100 if bib_count > 0 else 100.0
            # Read state.json
            quality_score = None
            gate_status = 'MISSING'
            state_path = os.path.join(path, '07-quality', 'state.json')
            if os.path.exists(state_path):
                try:
                    with open(state_path) as f:
                        state = json.load(f)
                    quality_score = state.get('quality_score')
                    gate_status = str(state.get('gate_status', 'MISSING'))
                except:
                    pass
            has_qc = os.path.exists(os.path.join(path, '07-quality', 'quality_check.md'))
            has_idx = os.path.exists(os.path.join(path, 'index.md'))
            fig_dir = os.path.join(path, '05-figures')
            fig_count = len([f for f in os.listdir(fig_dir) if f.startswith('Figure_')]) if os.path.isdir(fig_dir) else 0
            has_ga = os.path.exists(os.path.join(fig_dir, 'graphical_abstract.pdf')) if os.path.isdir(fig_dir) else False
            compile_pdf = os.path.join(mdir, tf.replace('.tex', '.pdf'))
            pdf_ok = os.path.exists(compile_pdf) and os.path.getsize(compile_pdf) > 500000
            # Score calculation
            score = 0
            if total_cites >= 50: score += 15
            elif total_cites >= 30: score += 10
            if d10a >= 95: score += 15
            elif d10a >= 80: score += 10
            elif d10a >= 60: score += 5
            if pdf_ok: score += 15
            if quality_score and quality_score >= 0.85: score += 15
            elif quality_score and quality_score >= 0.70: score += 10
            if has_qc: score += 10
            if has_idx: score += 5
            if has_ga: score += 5
            if fig_count >= 3: score += 10
            results.append({
                'name': name, 'tex': tf, 'cites': total_cites,
                'unique_keys': len(all_keys), 'bib': bib_count,
                'd10a': round(d10a, 1), 'qs': quality_score,
                'gate': gate_status, 'qc': has_qc, 'idx': has_idx,
                'figs': fig_count, 'ga': has_ga, 'pdf': pdf_ok, 'score': score,
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def print_report(results):
    """打印成熟度报告。"""
    print(f"{'论文':<40} {'引用':>4} {'Bib':>4} {'D10a':>5} {'QS':>5} {'Gate':>10} {'图':>2} {'GA':>2} {'PDF':>3} | 分")
    print("-" * 100)
    for r in results:
        qs_str = f"{r['qs']:.2f}" if r['qs'] is not None else "N/A"
        print(f"{r['name']:<40} {r['cites']:>4} {r['bib']:>4} {r['d10a']:>5.0f}% {qs_str:>5} {r['gate'][:10]:>10} {r['figs']:>2} {'Y' if r['ga'] else 'N':>2} {'Y' if r['pdf'] else 'N':>3} | {r['score']}")
    # Summary
    mature = [r for r in results if r['score'] >= 50]
    print(f"\n成熟论文 (≥50分): {len(mature)}")
    for r in mature:
        print(f"  ✅ {r['name']}: {r['score']}分")

if __name__ == '__main__':
    results = scan_papers(PAPERS_DIR)
    print_report(results)
