#!/usr/bin/env python3
# 原理绑定：SKILL.md 维度3-脚本可运行性，铁律：凡数必源，凡引必验
"""
Quality Gate Runner — 固定模板质量检查引擎
============================================
Synthos Quality Gate (正观) — 强制固定流程，零自由发挥。

用法:
    python3 quality-gate-runner.py --paper-dir <path> --output report.json
    python3 quality-gate-runner.py --paper-dir <path> --output report.json --mode fast    # 仅P0
    python3 quality-gate-runner.py --paper-dir <path> --output report.json --mode full    # 完整G1-G7

流程:
    G1 身份 → G2 编译 → G3 引用完整性 → G4 宪法合规 → G5 引用质量 → G6 影响映射 → G7 内容评审

输入:
    paper_dir — 论文目录，包含 paper.tex, paper.bib (可选), state.json (可选), .tex/ figures/

输出:
    JSON 报告 — 每门 PASS/FAIL/SCORE，P0/P1/P2 问题列表，修复建议
"""

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GateResult:
    gate: str
    pass_: bool
    score: float          # 0.0 - 1.0
    findings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self):
        d = {"gate": self.gate, "pass": self.pass_, "score": round(self.score, 4)}
        if self.findings:
            d["findings"] = self.findings
        if self.suggestions:
            d["suggestions"] = self.suggestions
        return d


@dataclass
class QualityReport:
    paper_dir: str
    paper_name: str
    overall_pass: bool
    overall_score: float
    gates: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "paper_dir": self.paper_dir,
            "paper_name": self.paper_name,
            "overall_pass": self.overall_pass,
            "overall_score": round(self.overall_score, 4),
            "gates": self.gates,
            "issues": self.issues,
        }


def read_file_safe(path: str) -> Optional[str]:
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return None



def find_tex_files(paper_dir: str):
    """Find .tex files recursively in paper_dir, skipping pdfs/.git/_archive."""
    results = []
    for root, dirs, files in os.walk(paper_dir):
        dirs[:] = [d for d in dirs if d not in ("pdfs", ".git", "_archive", "__pycache__")]
        for f in files:
            if f.endswith(".tex"):
                results.append(os.path.join(root, f))
    return results


def find_bib_files(paper_dir: str):
    """Find .bib files recursively in paper_dir."""
    results = []
    for root, dirs, files in os.walk(paper_dir):
        dirs[:] = [d for d in dirs if d not in ("pdfs", ".git", "_archive", "__pycache__")]
        for f in files:
            if f.endswith(".bib"):
                results.append(os.path.join(root, f))
    return results



def check_g1_identity(paper_dir: str) -> GateResult:
    """G1: 身份检查 — AGENT_MANIFEST.yaml present and valid.
    Checks paper_dir directly, then recurses into subdirectories."""
    manifest_path = os.path.join(paper_dir, "AGENT_MANIFEST.yaml")
    manifest = read_file_safe(manifest_path)
    
    if not manifest:
        # Look in subdirectories
        for root, dirs, files in os.walk(paper_dir):
            dirs[:] = [d for d in dirs if d not in ("pdfs", ".git", "_archive", "__pycache__")]
            if "AGENT_MANIFEST.yaml" in files:
                manifest_path = os.path.join(root, "AGENT_MANIFEST.yaml")
                manifest = read_file_safe(manifest_path)
                if manifest:
                    break

    if not manifest:
        return GateResult("G1_identity", False, 0.0, [
            "Missing AGENT_MANIFEST.yaml"
        ], ["Create AGENT_MANIFEST.yaml with agent.name, agent.framework, agent.capability"])

    return GateResult("G1_identity", True, 1.0)


def check_g2_compile(paper_dir: str) -> GateResult:
    """G2: 编译检查 — tex 文件语法合法性 + pdflatex 真编译。

    2026-09-07 reward-integrity (评审实验1): 旧实现只查 \\documentclass 等
    结构字符串, "有标记" 被当成 "能编译"。现 pdflatex 可用时执行真编译,
    退出码非 0 即 FAIL (结构检查保留为前置, 编译是裁决)。
    pdflatex 不可用时降级为纯结构检查并在 findings 标注 (不静默)。
    """
    import shutil
    import subprocess
    import tempfile

    tex_files = [f for f in os.listdir(paper_dir) if f.endswith(".tex")]
    if not tex_files:
        return GateResult("G2_compile", False, 0.0, [
            "No .tex files found"
        ], ["Create paper.tex"])

    # Check basic TeX structure
    tex_content = read_file_safe(os.path.join(paper_dir, tex_files[0])) or ""
    checks = {
        "document_begin": "\\documentclass" in tex_content or "\\documentstyle" in tex_content,
        "document_begin_end": "\\begin{document}" in tex_content and "\\end{document}" in tex_content,
        "has_title": "\\title" in tex_content,
    }

    passed = sum(checks.values())
    total = len(checks)
    score = passed / total if total > 0 else 0
    failures = [f"Missing {k}" for k, v in checks.items() if not v]

    if passed != total:
        return GateResult("G2_compile", False, score, failures,
                          ["Fix missing LaTeX structure elements"])

    # 真编译 (pdflatex 可用时)
    if shutil.which("pdflatex") is None:
        return GateResult("G2_compile", True, 1.0,
                          ["pdflatex not available — structure-only check (降级)"], [])

    log_tail = ""
    # cwd = 论文根 (paper_dir 的上一级): 相对路径 ../05-figures 等才能解析;
    # 输出隔离到 tmp, 不污染工作区。pdflatex 失败再试 xelatex (xeCJK 论文)。
    src = os.path.join(paper_dir, tex_files[0])
    workdir = os.path.dirname(os.path.abspath(paper_dir))
    with tempfile.TemporaryDirectory(prefix="g2_compile_") as tmp:
        proc = None
        for engine in ("pdflatex", "xelatex"):
            if shutil.which(engine) is None:
                continue
            proc = subprocess.run(
                [engine, "-interaction=nonstopmode", "-halt-on-error",
                 "-draftmode", "-output-directory", tmp, src],
                capture_output=True, text=True, timeout=180, cwd=workdir)
            if proc.returncode == 0:
                break
        logf = os.path.join(tmp, os.path.splitext(tex_files[0])[0] + ".log")
        if os.path.exists(logf):
            lines = (read_file_safe(logf) or "").splitlines()
            err_lines = [l for l in lines if l.startswith("!")]
            log_tail = "; ".join(err_lines[:3]) or lines[-1][:200]

    if proc.returncode != 0:
        detail = log_tail or (proc.stdout.strip().splitlines() or [""])[-1][:200] or proc.stderr.strip()[:200] or "compile failed"
        return GateResult("G2_compile", False, 0.5,
                          [f"compile exit={proc.returncode}: {detail[:300]}"],
                          ["Fix LaTeX compile errors (见 .log 首条 !)"])
    return GateResult("G2_compile", True, 1.0,
                      [f"pdflatex exit=0 ({tex_files[0]})"], [])


def check_g3_citation_integrity(paper_dir: str) -> GateResult:
    """G3: 引用完整性 — cite{} 与 bibitem 匹配。"""
    tex_files = [f for f in os.listdir(paper_dir) if f.endswith(".tex")]
    if not tex_files:
        return GateResult("G3_citation", False, 0.0, ["No .tex files"])

    tex = read_file_safe(os.path.join(paper_dir, tex_files[0])) or ""

    # Extract \cite keys (handles \cite, \citep, \citet, \citealp)
    cite_keys = set()
    for m in re.finditer(r'\\cite[a-zA-Z]*\{([^}]*)\}', tex):
        cite_keys.update(k.strip() for k in m.group(1).split(','))
    # Clean up malformed patterns: strip leading '{' from unclosed braces like \cite{key
    cite_keys = {k.lstrip('{') for k in cite_keys}
    # Remove keys that are just template placeholders
    cite_keys = {k for k in cite_keys if not k.startswith('<') and k != 'label' and k != 'lamport94'}

    # Look for bibliography files — find the one that matches best
    all_bib_paths = []
    # Manuscript dir
    for ff in os.listdir(paper_dir):
        if ff.endswith('.bib'):
            all_bib_paths.append(os.path.join(paper_dir, ff))
    # 06-references, 08-refs, etc. under manuscript dir
    for sub in ["06-references", "08-refs"]:
        p = os.path.join(paper_dir, sub)
        if os.path.isdir(p):
            for ff in os.listdir(p):
                if ff.endswith('.bib'):
                    all_bib_paths.append(os.path.join(p, ff))
    # Parent dir and grandparent
    parent_dir = os.path.dirname(paper_dir)
    for sub in ["06-references", "08-refs", "08-records"]:
        p = os.path.join(parent_dir, sub)
        if os.path.isdir(p):
            for ff in os.listdir(p):
                if ff.endswith('.bib'):
                    all_bib_paths.append(os.path.join(p, ff))
    
    # Also scan entire paper directory tree
    paper_root = os.path.dirname(paper_dir)
    for root, dirs, files in os.walk(paper_root):
        for ff in files:
            if ff.endswith('.bib'):
                fp = os.path.join(root, ff)
                if fp not in all_bib_paths:
                    all_bib_paths.append(fp)
    
    # Find the bib that matches the most cite keys
    best_keys = set()
    best_match = 0
    seen_bib = set()
    for bib_path in all_bib_paths:
        if bib_path in seen_bib:
            continue
        seen_bib.add(bib_path)
        bib = read_file_safe(bib_path)
        if not bib:
            continue
        bib_keys_set = set(re.findall(r'@\w+\{([^,\s]+)', bib))
        bib_keys_set.update(set(re.findall(r'\\bibitem\{(\w+)', bib)))
        overlap = len(bib_keys_set & cite_keys)
        if overlap > best_match:
            best_match = overlap
            best_keys = bib_keys_set
    
    bib_keys = best_keys if best_keys else set()
    
    if not bib_keys:
        # Fall back to inline thebibliography
        bib_keys = set(re.findall(r'\\bibitem\{(\w+)', tex))

    if not cite_keys:
        return GateResult("G3_citation", True, 1.0, [], ["No citations found — acceptable"])

    if not bib_keys:
        return GateResult("G3_citation", False, 0.0, [
            "No bibliography found"
        ], ["Add paper.bib with matching keys"])

    orphaned = cite_keys - bib_keys
    missing_refs = bib_keys - cite_keys

    if not orphaned and not missing_refs:
        return GateResult("G3_citation", True, 1.0, [], [])

    findings = []
    suggestions = []
    if orphaned:
        findings.append(f"Orphan citations (in .tex but not in .bib): {', '.join(sorted(orphaned)[:10])}")
        suggestions.append("Add missing bib entries")
    if missing_refs:
        findings.append(f"Unused bib entries: {', '.join(sorted(missing_refs)[:10])}")
        suggestions.append("Remove unused entries or cite them")

    match_rate = 1.0 - (len(orphaned) / len(cite_keys)) if cite_keys else 1.0
    return GateResult("G3_citation", match_rate >= 0.5, match_rate, findings, suggestions)


def check_g4_constitution(paper_dir: str) -> GateResult:
    """G4: 宪法合规 — 不违反 P0-P3 原则。"""
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    issues = []
    patterns = [
        (r'sk-[A-Za-z0-9]{20,}', 'Hardcoded API key pattern'),
        (r'password\s*=\s*["\x27][^"\x27]+["\x27]', 'Hardcoded password'),
    ]
    for pattern, desc in patterns:
        matches = re.findall(pattern, tex)
        if matches:
            issues.append(f"{desc}: {len(matches)} occurrence(s)")

    # Phone number check with academic false-positive filtering
    # Also check DOI context to avoid matching DOI substrings
    phone_matches = re.findall(r'\d{3}[-.]?\d{3}[-.]?\d{4}', tex)
    if phone_matches:
        # Filter academic patterns + DOI context
        filtered = []
        for m in phone_matches:
            if any(re.search(p, m) for p in [r's\d+-\d+-\d+', r'\d{7,}', r'\d{4}\u2013\d{4}', r'\d{3}\(\d', r'PMID', r'arXiv', r'\d{4};\d', r'\d{4}-\d{3}X?', r'ISSN', r'00\d{4}-']):
                continue
            # Check if this match is part of a DOI or URL by scanning context
            idx = tex.find(m)
            if idx > 0 and (tex[idx-1].isdigit() or tex[idx-1] in '/:.'):
                continue  # Likely part of a DOI, ISSN, or URL
            # Also check if the match is surrounded by longer numeric DOI strings
            if idx >= 0:
                # Check 20 chars before for DOI prefix
                before = tex[max(0,idx-20):idx]
                if any(c in before for c in ['doi', 'DOI', '10.', 'dx.doi', 'dx.doi.org']):
                    continue
            if 'http' in m or '%' in m or 'doi.org' in m:
                continue
            filtered.append(m)
        if filtered:
            issues.append(f"Potential phone number: {len(filtered)} occurrence(s)")

    has_no_credentials = len(issues) == 0
    score = 1.0 if has_no_credentials else 0.0
    return GateResult("G4_constitution", has_no_credentials, score, issues,
                      ["Remove hardcoded credentials, use environment variables"])

def check_g5_citation_quality(paper_dir: str) -> GateResult:
    """G5: 引用质量 — 检查 cite{} 与 bib 条目的匹配率，支持外部 .bib 文件。"""
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        return GateResult("G5_quality", False, 0.0, ["No .tex"])

    # 1. Extract ALL cite keys from paper.tex (handles cite{a,b,c} and \cite{a})
    cite_keys = set()
    for m in re.finditer(r'\\cite[{}\w]*\{([^}]+)\}', tex):
        for key in m.group(1).split(','):
            k = key.strip()
            if k:
                cite_keys.add(k)

    # 2. Check for \bibliography{} → find external .bib file
    bib_refs = re.findall(r'\\bibliography\{([^}]+)\}', tex)
    
    all_bib_keys = set()
    found_bib_file = False
    
    def extract_bib_keys_from_file(filepath):
        keys = set()
        with open(filepath) as f:
            content = f.read()
        # @article{key, or @misc{key, etc.
        keys.update(re.findall(r'@\w+\{([^,\s]+)', content))
        # \bibitem{key,
        keys.update(re.findall(r'\\bibitem\{(\w+)', content))
        return keys
    
    for bib_ref in bib_refs:
        # Try direct path
        for ext in ['', '.bib']:
            bib_path = os.path.join(paper_dir, bib_ref + ext)
            if os.path.exists(bib_path):
                found_bib_file = True
                all_bib_keys.update(extract_bib_keys_from_file(bib_path))
        
        # Also check one level up from paper_dir
        parent_dir = os.path.dirname(paper_dir)
        for ext in ['', '.bib']:
            bib_path = os.path.join(parent_dir, bib_ref + ext)
            if os.path.exists(bib_path):
                found_bib_file = True
                all_bib_keys.update(extract_bib_keys_from_file(bib_path))

    # 3. Also check for inline thebibliography
    inline_bibs = re.findall(r'\\bibitem\{([^}]+)\}', tex)
    for k in inline_bibs:
        all_bib_keys.add(k.strip())

    # 5. Also scan all .bib files within paper_root only
    # Find the bib that matches the MOST cite keys (best match strategy)
    best_keys = set()
    best_overlap = 0
    paper_root = os.path.dirname(paper_dir)  # FIX 2026-08-16: paper_dir is 01-manuscript, one dirname = single paper dir (was two, scanned all 280 papers' .bib and matched wrong paper)
    for root, dirs, files in os.walk(paper_root):
        # Limit depth: only go into manuscript, 06-references, 08-refs, 08-records, 08-refs
        rel = os.path.relpath(root, paper_root)
        if rel == '.' or (rel.count(os.sep) <= 1 and not rel.startswith('06') and not rel.startswith('08')):
            pass  # allowed
        elif rel.count(os.sep) > 2:
            continue  # too deep
        # Skip quality report dirs
        if any(d in root for d in ['07-quality', '.evolution', '03-code', '04-data', '05-figures']):
            continue
        for ff in files:
            if ff.endswith('.bib'):
                fp = os.path.join(root, ff)
                # Skip large files (>5MB)
                try:
                    if os.path.getsize(fp) > 5 * 1024 * 1024:
                        continue
                except:
                    pass
                try:
                    keys = extract_bib_keys_from_file(fp)
                    overlap = len(keys & cite_keys)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_keys = keys
                except:
                    pass
    
    if best_keys:
        all_bib_keys = best_keys

    # 5. Compute match rate
    if not cite_keys:
        return GateResult("G5_quality", True, 1.0, [], ["No citations — acceptable"])

    # A cite is "matched" if there exists any bib key containing it or vice versa
    matched = 0
    for ck in cite_keys:
        for bk in all_bib_keys:
            if ck in bk or bk in ck:
                matched += 1
                break

    match_rate = matched / len(cite_keys) if cite_keys else 1.0
    match_rate = min(match_rate, 1.0)
    adequate = match_rate >= 0.5

    findings = []
    suggestions = []
    if not found_bib_file and not inline_bibs and all_bib_keys:
        findings.append(f"Matched {matched}/{len(cite_keys)} cite keys to {len(all_bib_keys)} bib entries")
    else:
        findings.append(f"Citation match rate: {match_rate:.0%} ({matched}/{len(cite_keys)} matched)")
    
    if not adequate:
        unmatched = [c for c in cite_keys if not any(c in b or b in c for b in all_bib_keys)]
        if unmatched:
            suggestions.append(f"Unmatched cite keys: {', '.join(unmatched[:5])}")
        suggestions.append("Ensure all claims have bib entries or remove uncited entries")

    return GateResult("G5_quality", adequate, round(match_rate, 2), findings, suggestions)


def check_g6_impact(paper_dir: str) -> GateResult:
    """G6: 影响映射 — 受影响的原子/技能已映射。"""
    # Structural: paper should reference which cognitive atoms it uses
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""

    # Check for methodology description (proxy for impact mapping)
    has_methods = "\\section*{Methods}" in tex or "\\section*{Methodology}" in tex or \
                  "\\section*{Method}" in tex or "\\subsection*{Methods}" in tex or \
                  "method" in tex.lower()

    score = 1.0 if has_methods else 0.5
    return GateResult("G6_impact", has_methods, score,
                      [] if has_methods else ["No Methods section found"],
                      ["Add Methods section describing approach"])


def check_g7_content(paper_dir: str) -> GateResult:
    """G7: 内容评审 — 结构完整性。"""
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        return GateResult("G7_content", False, 0.0, ["No .tex"])

    # Case-study / empirical papers: "Case Study"/"System" sections serve as
    # the method description; "Finding"/"Analysis" sections serve as results.
    required_sections = {
        "Introduction": ["\\section{Introduction}", "\\section*{Introduction}"],
        "Methods": ["\\section{Methods}", "\\section{Methodology}",
                    "\\section{Case Study", "\\section{System",
                    "\\section{Architecture}", "\\section{Observation"],
        "Results": ["\\section{Results}", "\\section{Experiments}",
                    "\\section{Finding", "\\section{Analysis",
                    "\\section{Evaluation}", "\\section{Assessment}"],
        "Discussion": ["\\section{Discussion}", "\\section{Conclusion}",
                       "\\section{Threats to Validity}"],
    }

    found = 0
    total = len(required_sections)
    missing = []

    for name, patterns in required_sections.items():
        if isinstance(patterns, list):
            if any(p in tex for p in patterns):
                found += 1
            else:
                missing.append(name)
        else:
            if patterns in tex:
                found += 1
            else:
                missing.append(name)

    score = found / total
    return GateResult(
        "G7_content",
        score >= 0.6,
        score,
        missing if missing else [],
        [f"Missing sections: {', '.join(missing)}"] if missing else []
    )


def check_l05_data_honesty(paper_dir: str) -> GateResult:
    """L0.5: 数据诚实门 — 凡数必源。"""
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        tex_files = find_tex_files(paper_dir)
        tex = read_file_safe(tex_files[0]) if tex_files else ""
    if not tex:
        return GateResult("L0.5", False, 0.0, ["No .tex"])

    # Extract numeric declarations
    # Match patterns like: 85.2%, 3.14, 1234, p < 0.001
    numeric_decls = re.findall(
        r'(\d+\.?\d*\s*%?|[pP]\s*[<=>]\s*\d+\.?\d*)', tex
    )

    if not numeric_decls:
        return GateResult("L0.5", True, 1.0, [], ["No numeric declarations — acceptable"])

    # 2026-09-07 reward-integrity (评审实验1): "有 state.json" 不等于 "数字有证据"。
    # 逐项核对: tex 中每个数值声明 (归一化后) 必须在 state.json 任一叶子值中出现。
    def _flatten(o):
        vals = []
        if isinstance(o, dict):
            for v in o.values():
                vals.extend(_flatten(v))
        elif isinstance(o, list):
            for v in o:
                vals.extend(_flatten(v))
        else:
            vals.append(o)
        return vals

    def _norm(x):
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            return f"{float(x):.4f}".rstrip("0").rstrip(".")
        s = str(x).replace(" ", "")
        m = re.search(r"(\d+\.?\d*)", s)
        return f"{float(m.group(1)):.4f}".rstrip("0").rstrip(".") if m else s.lower()

    decls = [d.replace(" ", "") for d in numeric_decls]
    # 只核可核对的纯数值声明 (p<0.001 类含运算符的保留, 不参与分母)
    checkable = [d for d in decls if re.fullmatch(r"\d+\.?\d*%?", d)]
    if not checkable:
        return GateResult("L0.5", True, 1.0, [], ["No plain-numeric claims to check"])

    state_path = os.path.join(os.path.dirname(paper_dir), "state.json")
    state = read_file_safe(state_path)
    if not state:
        state_path = os.path.join(paper_dir, "state.json")
        state = read_file_safe(state_path)

    if state:
        try:
            state_data = json.loads(state)
        except json.JSONDecodeError:
            state_data = None
        if isinstance(state_data, (dict, list)) and state_data:
            state_vals = {_norm(v) for v in _flatten(state_data)}
            matched = [d for d in checkable if _norm(d) in state_vals]
            frac = len(matched) / len(checkable)
            if frac >= 1.0:
                return GateResult("L0.5", True, 1.0,
                                  [f"All {len(checkable)} numeric claims cross-verified vs state.json"], [])
            if frac >= 0.5:
                return GateResult("L0.5", False, 0.4,
                                  [f"{len(checkable) - len(matched)}/{len(checkable)} numeric claims NOT found in state.json"],
                                  ["把未核对数值写入 state.json 或删除/改写为定性表述"])
            return GateResult("L0.5", False, 0.2 * frac + 0.0,
                              [f"Only {len(matched)}/{len(checkable)} numeric claims found in state.json"],
                              ["凡数必源: 每个数值写入 state.json 并附来源字段"])

    # 无 state.json (或空/损坏): 数值声明无证据源 → 不得按"通过"处理
    return GateResult("L0.5", False, 0.3,
                      [f"{len(checkable)} numeric claims, no state.json evidence source"],
                      ["Add state.json with the claimed values and their provenance"])


def check_g8_refs_digest(paper_dir: str) -> GateResult:
    """G8_refs_digest: 参考文献全文 digest 是否已生成 (GAP 前置机械门).

    规则写在 SKILL.md 是认知约束, 会被跳过。本门把全文研读变成文件存在性:
    04-data/references_digest.json 覆盖 >=80% 的 06-references PDF 且每篇有
    有效 abstract/conclusion 段才过。没有这个文件, GAP 就没有全文证据。
    """
    root = os.path.dirname(os.path.abspath(paper_dir))
    ref_pdfs = [os.path.basename(p)[:-4]
                for p in glob.glob(os.path.join(root, "06-references", "*.pdf"))]
    if not ref_pdfs:
        return GateResult("G8_refs_digest", True, 1.0,
                          ["no 06-references PDFs — digest not required"], [])
    dpath = os.path.join(root, "04-data", "references_digest.json")
    if not os.path.exists(dpath):
        return GateResult("G8_refs_digest", False, 0.0,
                          [f"references_digest.json missing ({len(ref_pdfs)} ref PDFs unread)"],
                          [f"run: python3 {os.path.join(os.path.dirname(__file__),'make_refs_digest.py')} --paper-dir {paper_dir}"])
    try:
        d = json.load(open(dpath))
    except Exception as e:
        return GateResult("G8_refs_digest", False, 0.0,
                          [f"digest unparseable: {e}"],
                          ["regenerate references_digest.json"])
    papers = d.get("papers", {})
    # 判据 = 全文 Markdown 是否落盘且实质可读 (>=2000 chars)，不是"正则找到标题"。
    # 标题格式因期刊而异，heading 正则必有漏检；全文存在性才是"读过"的诚实证据。
    md_dir = os.path.join(root, "04-data", "references-md")
    covered = []
    for k in ref_pdfs:
        p = papers.get(k, {})
        md_chars = p.get("chars", 0)
        mdp = os.path.join(md_dir, k + ".md")
        if os.path.exists(mdp):
            md_chars = max(md_chars, os.path.getsize(mdp))
        if md_chars >= 2000:
            covered.append(k)
    frac = len(covered) / len(ref_pdfs) if ref_pdfs else 0
    missing = [k for k in ref_pdfs if k not in covered]
    if frac >= 0.8:
        return GateResult("G8_refs_digest", True, 1.0,
                          [f"full-text digest covers {len(covered)}/{len(ref_pdfs)} ref PDFs ({frac:.0%})"],
                          [])
    return GateResult("G8_refs_digest", False, round(frac, 2),
                      [f"full-text digest covers only {len(covered)}/{len(ref_pdfs)} ({frac:.0%}); missing: {missing[:5]}"],
                      ["run make_refs_digest.py to convert all ref PDFs before GAP"])


def run_gate(paper_dir: str, mode: str = "full") -> QualityReport:
    """Run all gates in fixed order: G1 → G2 → G3 → G4 → G5 → G6 → G7 → G8 + L0.5"""
    paper_name = Path(paper_dir).name
    report = QualityReport(paper_dir, paper_name, True, 0.0)

    gates = {
        "G1_identity": check_g1_identity,
        "G2_compile": check_g2_compile,
        "G3_citation_integrity": check_g3_citation_integrity,
        "G4_constitution": check_g4_constitution,
        "G5_citation_quality": check_g5_citation_quality,
        "G6_impact": check_g6_impact,
        "G7_content": check_g7_content,
        "G8_refs_digest": check_g8_refs_digest,
        "L0.5_data_honesty": check_l05_data_honesty,
    }

    all_scores = []
    for gate_name, gate_fn in gates.items():
        result = gate_fn(paper_dir)
        report.gates[gate_name] = result.to_dict()
        all_scores.append(result.score)

        if not result.pass_:
            report.overall_pass = False
        if result.findings and not result.pass_:
            # 通过的门的 findings 是正面证据 (如 "Cross-referenced state.json")，
            # 不是问题——不计入 issues (cycle 273 修: L0.5 通过 findings 曾被误标 P0)
            report.issues.append({
                "gate": gate_name,
                "severity": "P0" if gate_name in ("L0.5_data_honesty", "G4_constitution", "G8_refs_digest") else "P1",
                "findings": result.findings,
                "suggestions": result.suggestions,
            })

    report.overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

    # L0.5 is a一票否决
    if report.gates.get("L0.5_data_honesty", {}).get("score", 1.0) < 0.5:
        report.overall_pass = False

    # G8_refs_digest 一票否决 (2026-08-31 用户裁决): 全文没读 = 证据不完整 = 造假嫌疑。
    # 参考文献论文不读全文就提 GAP/假设, 与 data honesty 同级。
    if report.gates.get("G8_refs_digest", {}).get("pass", True) is False:
        report.overall_pass = False

    return report


def main():
    parser = argparse.ArgumentParser(description="Quality Gate Runner")
    parser.add_argument("--paper-dir", required=True, help="Paper directory")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--mode", choices=["fast", "full"], default="full",
                        help="Fast = G1+G2+L0.5 only. Full = all G1-G7 + L0.5")
    args = parser.parse_args()

    if not os.path.isdir(args.paper_dir):
        print(f"Error: {args.paper_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    report = run_gate(args.paper_dir, mode=args.mode)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Paper: {report.paper_name}")
    print(f"Overall: {report.overall_score:.0%} {'PASS' if report.overall_pass else 'FAIL'}")
    for gate_name, gate_data in report.gates.items():
        status = "✅" if gate_data["pass"] else "❌"
        print(f"  {gate_name}: {status} {gate_data['score']:.2f}")
    if report.issues:
        print(f"\nIssues ({len(report.issues)}):")
        for issue in report.issues:
            print(f"  [{issue['severity']}] {issue['gate']}: {'; '.join(issue['findings'])}")

    print(f"\nFull report: {args.output}")
    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
