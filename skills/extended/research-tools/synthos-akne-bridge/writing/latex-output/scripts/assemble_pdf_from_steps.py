#!/usr/bin/env python3
"""Assemble paper PDF from step_*.md files in Synthos manuscript structure."""
import os
import sys

def assemble_pdf(paper_dir, output_name="paper"):
    """
    paper_dir: path to 01-manuscript/ directory
    Reads step_gap_analysis.md through step_discussion.md (and optional ref_check, quality_check)
    Assembles into {output_name}.tex and compiles to {output_name}.pdf
    """
    steps_order = [
        "step_gap_analysis", "step_abstract", "step_intro",
        "step_method", "step_results", "step_discussion"
    ]
    
    tex_header = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{url}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{geometry}
\geometry{margin=1in}
\begin{document}
"""
    tex = tex_header
    
    for step in steps_order:
        step_file = os.path.join(paper_dir, f"{step}.md")
        if not os.path.exists(step_file):
            continue
        with open(step_file, "r") as f:
            content = f.read()
        in_latex = False
        for line in content.split("\n"):
            if line.strip() == "```latex":
                in_latex = True
                continue
            elif line.strip() == "```":
                in_latex = False
                continue
            elif in_latex:
                tex += line + "\n"
    
    # Optional: include ref_check and quality_check
    for extra_step in ["step_ref_check", "step_quality_check"]:
        extra_file = os.path.join(paper_dir, f"{extra_step}.md")
        if os.path.exists(extra_file):
            tex += f"\n\\section{{{'Reference Verification' if 'ref' in extra_step else 'Quality Assessment'}}}\n"
            with open(extra_file, "r") as f:
                for line in f:
                    stripped = line.strip()
                    # Skip markdown formatting, keep text content
                    if stripped and not stripped.startswith("#") and not stripped.startswith("|") and not stripped.startswith("-") and not stripped.startswith("`"):
                        if any(kw in stripped.lower() for kw in ["score", "pass", "dimension", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "pass", "complete", "verified"]):
                            tex += stripped + "\n"
    
    tex += "\n\\end{document}\n"
    
    tex_path = os.path.join(paper_dir, f"{output_name}.tex")
    with open(tex_path, "w") as f:
        f.write(tex)
    print(f"Wrote {len(tex)} chars to {tex_path}")
    
    # Compile with MiKTeX-compatible flag
    compile_cmd = f'cd {paper_dir} && pdflatex -interaction nonstopmode {output_name}.tex 2>&1 | tail -5'
    os.system(compile_cmd)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        assemble_pdf(sys.argv[1])
    else:
        print("Usage: python3 assemble_pdf.py <paper_dir>")
