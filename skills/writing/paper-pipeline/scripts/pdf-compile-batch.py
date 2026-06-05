#!/usr/bin/env python3
"""Batch compile PDFs for fully-complete papers that are missing their PDFs.

Usage:
    python3 pdf-compile-batch.py [--dry-run] [--output-dir /path]

Scans all paper directories, finds those with 8/8 completed steps but no PDF,
then compiles each one.
"""

import json
import glob
import os
import subprocess
import sys
import argparse
from pathlib import Path

PAPERS_DIR = os.environ.get(
    "SYNTHOS_PAPERS_DIR",
    "/media/yakeworld/sda2/Synthos/outputs/papers"
)

# 8 IMRaD pipeline steps in order
STEPS = [
    "gap_analysis", "abstract", "introduction", "method",
    "results", "discussion", "reference_check", "quality_check"
]

def find_incomplete_pdfs():
    """Find papers that are 100% complete but missing PDFs."""
    incomplete = []
    for state_file in glob.glob(os.path.join(PAPERS_DIR, "*/state.json")):
        name = os.path.basename(os.path.dirname(state_file))
        try:
            with open(state_file) as f:
                d = json.load(f)
            steps = d.get("steps_completed", [])
            if len(steps) < 8:
                continue  # Not complete yet

            # Check if a PDF exists in the paper directory
            paper_dir = os.path.dirname(state_file)
            has_pdf = any(
                f.endswith(".pdf")
                for f in os.listdir(paper_dir)
            )

            if not has_pdf:
                # Find the .tex file
                tex_file = None
                for candidate in [
                    os.path.join(paper_dir, "01-manuscript", "paper.tex"),
                    os.path.join(paper_dir, "paper.tex"),
                    os.path.join(paper_dir, "article.tex"),
                ]:
                    if os.path.exists(candidate):
                        tex_file = candidate
                        break

                if tex_file:
                    incomplete.append({
                        "name": name,
                        "dir": paper_dir,
                        "tex": tex_file,
                        "steps": len(steps),
                        "last_step": steps[-1] if steps else "",
                    })
        except Exception:
            continue
    return incomplete


def compile_paper(paper_info, dry_run=False):
    """Compile a single paper's LaTeX to PDF. Returns success status."""
    name = paper_info["name"]
    tex = paper_info["tex"]
    dir_path = paper_info["dir"]

    # Extract base name without extension for bibtex
    base = Path(tex).stem
    if base in ("paper", "article"):
        base = Path(Path(tex).parent).stem

    if dry_run:
        print(f"  [DRY-RUN] Would compile: {name}")
        return True

    results = []
    commands = [
        ["pdflatex", "-interaction=nonstopmode", tex],
        ["bibtex", base],
        ["pdflatex", "-interaction=nonstopmode", tex],
        ["pdflatex", "-interaction=nonstopmode", tex],
    ]

    for i, cmd in enumerate(commands):
        try:
            result = subprocess.run(
                cmd, cwd=dir_path, capture_output=True, text=True, timeout=120
            )
            results.append(result.returncode)
            if result.returncode != 0:
                # Check for actual errors in output
                if "!\\|\\|" in result.stderr or "Undefined control" in result.stderr:
                    print(f"  [FAIL] {name} step {i+1}/{len(commands)}: exit {result.returncode}")
                    return False
        except FileNotFoundError:
            print(f"  [SKIP] pdflatex not found for {name}")
            return False
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] {name} step {i+1}/{len(commands)}: timeout")
            return False

    # Check final output
    expected_pdf = os.path.join(dir_path, f"{name}.pdf")
    if os.path.exists(expected_pdf):
        size = os.path.getsize(expected_pdf)
        print(f"  [OK] {name}: {size//1024}KB PDF at {expected_pdf}")
        return True
    else:
        # Find any generated PDF
        pdfs = glob.glob(os.path.join(dir_path, "*.pdf"))
        if pdfs:
            print(f"  [OK] {name}: PDF generated ({pdfs[0]})")
            return True
        print(f"  [FAIL] {name}: no PDF found after compilation")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch compile PDFs")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be compiled")
    parser.add_argument("--count", type=int, default=5, help="Max papers to process")
    args = parser.parse_args()

    incomplete = find_incomplete_pdfs()
    print(f"Found {len(incomplete)} papers missing PDFs:")

    if not incomplete:
        print("All papers have PDFs! Nothing to do.")
        return

    for p in incomplete[:args.count]:
        print(f"  - {p['name']}: {p['steps']}/8 steps, tex={p['tex']}")

    if not args.dry_run:
        print("\nCompiling...")
        for p in incomplete[:args.count]:
            compile_paper(p, dry_run=False)
    else:
        print("\nDry run mode — no compilation performed.")


if __name__ == "__main__":
    main()
