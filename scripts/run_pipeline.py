#!/usr/bin/env python3
"""端到端管线执行器 — ACQ → EXT → ASC → HYP → ARG → VER

Usage:
  python3 run_pipeline.py --paper <paper_name>    # 处理指定论文
  python3 run_pipeline.py --all                   # 处理所有未完成论文
  python3 run_pipeline.py --resume                # 从断点继续

Each step checks upstream artifacts. If present, skip. If missing, execute.
"""
import json, os, re, sys, subprocess, time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')
QUEUE_FILE = os.path.join(PAPERS_DIR, 'paper-queue.json')

def log(msg, paper_id=None):
    prefix = f"[{paper_id}] " if paper_id else ""
    print(f"{prefix}{msg}")

def load_queue():
    with open(QUEUE_FILE) as f:
        return json.load(f)

def load_paper_trace(paper_id):
    trace_path = os.path.join(PAPERS_DIR, paper_id, 'pipeline_trace.json')
    if os.path.exists(trace_path):
        with open(trace_path) as f:
            return json.load(f)
    return None

def save_paper_trace(paper_id, trace):
    trace_path = os.path.join(PAPERS_DIR, paper_id, 'pipeline_trace.json')
    with open(trace_path, 'w') as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

def get_paper_dirs():
    """Get all paper directories with paper.tex."""
    papers = []
    for item in sorted(os.listdir(PAPERS_DIR)):
        full = os.path.join(PAPERS_DIR, item)
        if not os.path.isdir(full):
            continue
        if os.path.exists(os.path.join(full, '01-manuscript', 'paper.tex')):
            papers.append(item)
    return papers

def has_pdf(paper_id):
    paths = [
        f'{PAPERS_DIR}/{paper_id}/paper.pdf',
        f'{PAPERS_DIR}/{paper_id}/01-manuscript/paper.pdf',
        f'{PAPERS_DIR}/{paper_id}/02-submission/paper.pdf',
    ]
    return any(os.path.exists(p) for p in paths)

def has_quality(paper_id):
    return os.path.exists(f'{PAPERS_DIR}/{paper_id}/07-quality/final.json')

def step_acq(paper_id):
    """Step 1: ACQ - 知识获取. Check if PDF exists."""
    log("ACQ: Checking PDF availability...")
    if has_pdf(paper_id):
        log("  PDF found — ACQ already complete")
        return True
    log("  No PDF — needs manual download")
    return False

def step_ext(paper_id):
    """Step 2: EXT - 知识提取. Check if knowledge.json exists."""
    kpath = f'{PAPERS_DIR}/{paper_id}/07-quality/knowledge.json'
    if os.path.exists(kpath):
        log("EXT: knowledge.json found — already extracted")
        return True
    log("EXT: No knowledge.json — needs AI extraction (skip in batch mode)")
    return False

def step_asc(paper_id):
    """Step 3: ASC - 关联发现."""
    graph_path = f'{PAPERS_DIR}/{paper_id}/07-quality/knowledge_graph.json'
    if os.path.exists(graph_path):
        log("ASC: Knowledge graph found")
        return True
    log("ASC: No knowledge graph (requires cross-paper analysis)")
    return False

def step_arg(paper_id):
    """Step 4: ARG - 论证表达. Check if manuscript exists."""
    tex_path = f'{PAPERS_DIR}/{paper_id}/01-manuscript/paper.tex'
    if os.path.exists(tex_path):
        log("ARG: Manuscript found")
        return True
    log("ARG: No manuscript")
    return False

def step_ver(paper_id):
    """Step 5: VER - 观点验证. Check if G7 quality check passed."""
    fpath = f'{PAPERS_DIR}/{paper_id}/07-quality/final.json'
    if os.path.exists(fpath):
        with open(fpath) as f:
            data = json.load(f)
        if data.get('overall_pass', False):
            log("VER: G7 passed")
            return True
        log(f"VER: G7 score={data.get('overall_score', 'N/A')}")
    log("VER: No quality check")
    return False

def run_papers(paper_ids=None):
    """Run pipeline check on specified papers."""
    if paper_ids is None:
        paper_ids = get_paper_dirs()

    results = {'completed': [], 'partial': [], 'incomplete': []}

    for pid in paper_ids:
        log(f"\n{'='*50}")
        log(f"Pipeline Check: {pid}")

        trace = load_paper_trace(pid)
        steps = ['acq', 'ext', 'asc', 'arg', 'ver']
        step_results = {}

        for step in steps:
            fn = globals()[f'step_{step}']
            result = fn(pid)
            step_results[step] = result

        # Update trace
        if trace:
            trace['pipeline_steps'] = step_results
            trace['last_check'] = datetime.now().isoformat()
            save_paper_trace(pid, trace)

        # Classify
        all_pass = all(step_results.values())
        any_pass = any(step_results.values())

        if all_pass:
            results['completed'].append(pid)
        elif any_pass:
            results['partial'].append(pid)
        else:
            results['incomplete'].append(pid)

    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Synthos Pipeline Runner')
    parser.add_argument('--paper', type=str, help='Process specific paper')
    parser.add_argument('--all', action='store_true', help='Process all papers')
    parser.add_argument('--resume', action='store_true', help='Resume from last incomplete')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    if args.paper:
        results = run_papers([args.paper])
    elif args.all or args.resume:
        if args.resume:
            # Only process partial papers
            all_ids = get_paper_dirs()
            partial = []
            for pid in all_ids:
                trace = load_paper_trace(pid)
                if trace and not all(trace.get('pipeline_steps', {}).values()):
                    partial.append(pid)
            results = run_papers(partial if partial else all_ids)
        else:
            results = run_papers()
    else:
        print("Usage: python3 run_pipeline.py [--paper NAME] [--all] [--resume]")
        print()
        print("Options:")
        print("  --paper NAME   Check pipeline for a specific paper")
        print("  --all          Check all papers")
        print("  --resume       Resume from last incomplete paper")
        print("  --json         Output results as JSON")
        sys.exit(0)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*50}")
        print("Pipeline Check Results:")
        print(f"  Completed (all steps): {len(results['completed'])}")
        print(f"  Partial (some steps):  {len(results['partial'])}")
        print(f"  Incomplete (none):     {len(results['incomplete'])}")

if __name__ == '__main__':
    main()
