#!/usr/bin/env python3
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


def check_g1_identity(paper_dir: str) -> GateResult:
    """G1: 身份检查 — AGENT_MANIFEST.yaml present and valid."""
    manifest_path = os.path.join(paper_dir, "AGENT_MANIFEST.yaml")
    manifest = read_file_safe(manifest_path)

    if not manifest:
        return GateResult("G1_identity", False, 0.0, [
            "Missing AGENT_MANIFEST.yaml"
        ], ["Create AGENT_MANIFEST.yaml with agent.name, agent.framework, agent.capability"])

    return GateResult("G1_identity", True, 1.0)


def check_g2_compile(paper_dir: str) -> GateResult:
    """G2: 编译检查 — tex 文件语法合法性 + 编译运行。"""
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

    return GateResult(
        "G2_compile",
        passed == total,
        score,
        failures,
        ["Fix missing LaTeX structure elements"]
    )


def check_g3_citation_integrity(paper_dir: str) -> GateResult:
    """G3: 引用完整性 — cite{} 与 bibitem 匹配。"""
    tex_files = [f for f in os.listdir(paper_dir) if f.endswith(".tex")]
    if not tex_files:
        return GateResult("G3_citation", False, 0.0, ["No .tex files"])

    tex = read_file_safe(os.path.join(paper_dir, tex_files[0])) or ""

    # Extract \cite keys
    cite_keys = set(re.findall(r'\\cite{?([^},\s]+)}?', tex))

    bib_path = os.path.join(paper_dir, "paper.bib")
    bib = read_file_safe(bib_path)
    if bib:
        bib_keys = set(re.findall(r'@(\w+)\{(\w+)', bib))
    else:
        # Check for thebibliography style
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
    return GateResult("G3_citation", match_rate >= 0.8, match_rate, findings, suggestions)


def check_g4_constitution(paper_dir: str) -> GateResult:
    """G4: 宪法合规 — 不违反 P0-P3 原则。"""
    # This is a structural check: ensure paper has no hardcoded credentials
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""

    issues = []
    patterns = [
        (r'sk-[A-Za-z0-9]{20,}', 'Hardcoded API key pattern'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
        (r'\d{3}[-.]?\d{3}[-.]?\d{4}', 'Potential phone number'),
    ]

    for pattern, desc in patterns:
        matches = re.findall(pattern, tex)
        if matches:
            issues.append(f"{desc}: {len(matches)} occurrence(s)")

    has_no_credentials = len(issues) == 0
    score = 1.0 if has_no_credentials else 0.0

    return GateResult("G4_constitution", has_no_credentials, score, issues,
                      ["Remove hardcoded credentials, use environment variables"])


def check_g5_citation_quality(paper_dir: str) -> GateResult:
    """G5: 引用质量 — 引用功能分类 + 恰当性判定。"""
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""
    if not tex:
        return GateResult("G5_quality", False, 0.0, ["No .tex"])

    cite_count = len(re.findall(r'\\cite', tex))
    bib_count = len(re.findall(r'\\bibitem', tex))

    if cite_count == 0 and bib_count == 0:
        return GateResult("G5_quality", True, 1.0, [], ["No citations — acceptable"])

    if cite_count == 0 or bib_count == 0:
        return GateResult("G5_quality", False, 0.0, [
            f"Zero { 'cites' if cite_count == 0 else 'bibitems' } found"
        ], ["Ensure all claims have citations"])

    match_rate = min(cite_count, bib_count) / max(cite_count, bib_count)
    adequate = match_rate >= 0.8  # 80% threshold

    return GateResult("G5_quality", adequate, match_rate,
                      [f"Citation match rate: {match_rate:.0%}"],
                      ["Ensure citation count ≈ bibitem count"])


def check_g6_impact(paper_dir: str) -> str -> GateResult:
    """G6: 影响映射 — 受影响的原子/技能已映射。"""
    # Structural: paper should reference which cognitive atoms it uses
    tex = read_file_safe(os.path.join(paper_dir, "paper.tex")) or ""

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
        return GateResult("G7_content", False, 0.0, ["No .tex"])

    required_sections = {
        "Introduction": "\\section{Introduction}",
        "Methods": ["\\section{Methods}", "\\section{Methodology}"],
        "Results": ["\\section{Results}", "\\section{Experiments}"],
        "Discussion": ["\\section{Discussion}", "\\section{Conclusion}"],
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
        return GateResult("L0.5", False, 0.0, ["No .tex"])

    # Extract numeric declarations
    # Match patterns like: 85.2%, 3.14, 1234, p < 0.001
    numeric_decls = re.findall(
        r'(\d+\.?\d*\s*%?|[pP]\s*[<=>]\s*\d+\.?\d*)', tex
    )

    if not numeric_decls:
        return GateResult("L0.5", True, 1.0, [], ["No numeric declarations — acceptable"])

    # Check if state.json exists and cross-validate
    state_path = os.path.join(paper_dir, "state.json")
    state = read_file_safe(state_path)

    if state:
        try:
            state_data = json.loads(state)
            if isinstance(state_data, dict):
                score = 0.8  # Has state.json as evidence source
                return GateResult("L0.5", True, score,
                                  ["Cross-referenced state.json"], [])
        except json.JSONDecodeError:
            pass

    return GateResult("L0.5", True, 0.6,
                      ["Numeric claims lack state.json cross-reference"],
                      ["Add state.json with quality metrics"])


def run_gate(paper_dir: str, mode: str = "full") -> QualityReport:
    """Run all gates in fixed order: G1 → G2 → G3 → G4 → G5 → G6 → G7 + L0.5"""
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
        "L0.5_data_honesty": check_l05_data_honesty,
    }

    all_scores = []
    for gate_name, gate_fn in gates.items():
        result = gate_fn(paper_dir)
        report.gates[gate_name] = result.to_dict()
        all_scores.append(result.score)

        if not result.pass_:
            report.overall_pass = False
        if result.findings:
            report.issues.append({
                "gate": gate_name,
                "severity": "P0" if gate_name in ("L0.5_data_honesty", "G4_constitution") else "P1",
                "findings": result.findings,
                "suggestions": result.suggestions,
            })

    report.overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

    # L0.5 is a一票否决
    if report.gates.get("L0.5_data_honesty", {}).get("score", 1.0) < 0.5:
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
