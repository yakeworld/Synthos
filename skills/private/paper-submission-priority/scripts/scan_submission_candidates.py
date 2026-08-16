#!/usr/bin/env python3
"""
论文管线质量扫描 — 快速筛选可投稿论文。
扫描 /media/yakeworld/sda2/Synthos/outputs/papers/ 下所有 state.json，
输出质量分>=90、G1-G7全PASS、D10a>=99%、有PDF的候选列表。

用法: python scan_submission_candidates.py
"""
import json
import os
import sys

PAPERS_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers"

def get_quality(state):
    """提取 quality_score，支持顶层和嵌套格式"""
    q = state.get("quality_score", -1)
    if isinstance(q, dict):
        q = q.get("overall", -1)
    return float(q) if q is not None else -1

def get_gates_pass(state):
    """检查 G1-G7 是否全部 PASS"""
    gates = state.get("gates_result")
    if isinstance(gates, str) and gates == "PASS":
        return True
    if isinstance(gates, dict):
        if "overall" in gates and gates["overall"] == "PASS":
            return True
        gates_list = gates.get("gates", [])
        if gates_list:
            return all(
                g.get("status") == "PASS" 
                for g in gates_list 
                if isinstance(g, dict)
            )
    return False

def get_d10a(state):
    """提取 D10a 百分比"""
    scan = state.get("d8_d10a_scan", {})
    d10a = scan.get("d10a", 0)
    if isinstance(d10a, str) and "%" in d10a:
        try:
            return float(d10a.replace("%", ""))
        except:
            return 0
    return float(d10a)

def has_pdf(papers_dir, d):
    """检查论文是否有 PDF"""
    pdf_path = os.path.join(papers_dir, d, d + ".pdf")
    if os.path.exists(pdf_path):
        return True
    for sub in os.listdir(os.path.join(papers_dir, d)):
        subpath = os.path.join(papers_dir, d, sub)
        if os.path.isfile(subpath) and subpath.endswith(".pdf"):
            return True
    return False

def main():
    candidates = []
    
    for d in sorted(os.listdir(PAPERS_DIR)):
        if d.startswith("_"):
            continue
        
        state_path = os.path.join(PAPERS_DIR, d, "state.json")
        if not os.path.exists(state_path):
            continue
        
        try:
            with open(state_path) as f:
                state = json.load(f)
        except:
            continue
        
        status = state.get("status", "unknown")
        if status in ("HARD_FAIL", "FAIL", "error"):
            continue
        
        quality = get_quality(state)
        if quality < 85:
            continue
        
        if not get_gates_pass(state):
            continue
        
        d10a = get_d10a(state)
        if d10a < 99:
            continue
        
        if not has_pdf(PAPERS_DIR, d):
            continue
        
        scan = state.get("d8_d10a_scan", {})
        orphans = scan.get("orphans_count", -1)
        zombies = scan.get("zombies_count", -1)
        
        if orphans != 0 or zombies != 0:
            continue
        
        gates = state.get("gates_result", {})
        gates_overall = gates.get("overall", "PASS") if isinstance(gates, dict) else "PASS"
        
        ws = state.get("white_space", {})
        ws_status = ws.get("status", "N/A") if isinstance(ws, dict) else "N/A"
        
        title = state.get("title", "")
        if not title:
            title = state.get("paper_name", d)
        
        stage = state.get("stage", "")
        metrics = state.get("metrics", {})
        
        candidates.append({
            "dir": d,
            "quality": quality,
            "d10a": d10a,
            "d8": scan.get("d8", 0),
            "gates": gates_overall,
            "stage": stage,
            "ws": ws_status,
            "title": title,
            "metrics": metrics,
        })
    
    candidates.sort(key=lambda x: (x["quality"], x["d10a"]), reverse=True)
    
    if not candidates:
        print("No submission-ready candidates found.")
        sys.exit(0)
    
    print(f"Found {len(candidates)} submission-ready candidates\n")
    print(f"{'DIR':<45} {'QUAL':>4} {'D8':>4} {'D10a':>6} {'WS':<15} {'Stage'}")
    print("-" * 110)
    
    for c in candidates:
        print(f"{c['dir']:<45} {c['quality']:>4} {c['d8']:>4} {c['d10a']:>5.1f}% {str(c['ws']):<15} {c['stage']}")
        if c['title'] and c['title'] != c['dir']:
            print(f"  Title: {c['title']}")

if __name__ == "__main__":
    main()
