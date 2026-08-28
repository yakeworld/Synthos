#!/usr/bin/env python3
"""gene_trace.py — 行为留痕 CLI (cycle 268, behavior 维的执行层)

存在即留痕, 无痕即未生。
一条命令 = 一条 gene_activation 记录 = behavior 维 activation_pct 的分子。

用法:
  gene_trace.py add EVOL-001 EVOL-007 --task "论文管线审计"
  gene_trace.py add TR-001 --task "快速检索" --trace /path/to/pipeline_trace.json
  gene_trace.py last        # 看最近 5 条留痕

默认输出: outputs/_runtime/pipeline_trace_auto_<ts>.json (匹配 diagnose 的 glob)
指定 --trace 则追加进已有 trace (合并 activated, 不覆盖)。
"""
import json, os, sys, time
from datetime import datetime

BASE = os.environ.get('SYNTHOS_DIR', '/media/yakeworld/sda2/Synthos')
RUNTIME = os.path.join(BASE, 'outputs', '_runtime')

def cmd_add(genes, task, trace_path):
    ts = time.strftime('%Y-%m-%dT%H:%M:%S')
    if trace_path:
        p = trace_path
        d = {}
        if os.path.exists(p):
            try:
                d = json.load(open(p))
            except Exception:
                print(f"WARN: {p} 不可解析, 重建", file=sys.stderr)
        ga = d.get('gene_activation') or {}
        act = set(ga.get('activated', [])) | set(genes)
        ga.update({"activated": sorted(act), "ts": ts,
                   "reason": task or ga.get('reason', '')})
        d['gene_activation'] = ga
        d.setdefault('atoms', {}).setdefault('gene-activation', {
            "status": "completed", "honesty_notes": ["gene_trace.py 留痕"]})
        d.setdefault('ts', ts)
        os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    else:
        os.makedirs(RUNTIME, exist_ok=True)
        stem = time.strftime('pipeline_trace_auto_%Y%m%d_%H%M%S')
        p = os.path.join(RUNTIME, stem + f'_{len(genes)}g.json')
        d = {
            "session_id": stem,
            "query": task or '(gene activation record)',
            "atoms": {"gene-activation": {"status": "completed",
                                          "honesty_notes": ["gene_trace.py 留痕"]}},
            "gene_activation": {"activated": sorted(genes), "ts": ts, "reason": task or ''},
            "ts": ts,
        }
    json.dump(d, open(p, 'w'), ensure_ascii=False, indent=1)
    # 同步留痕副本 (JSONL, 人类可读流水)
    log = os.path.join(RUNTIME, 'gene_activations.jsonl')
    with open(log, 'a') as f:
        f.write(json.dumps({"ts": ts, "genes": sorted(genes), "task": task or '',
                            "trace": p}, ensure_ascii=False) + '\n')
    print(f"留痕 {len(genes)} 基因 → {p}")
    return 0

def cmd_last():
    log = os.path.join(RUNTIME, 'gene_activations.jsonl')
    if not os.path.exists(log):
        print("无留痕 (outputs/_runtime/gene_activations.jsonl 不存在)"); return 0
    lines = [l for l in open(log) if l.strip()][-5:]
    for l in lines:
        r = json.loads(l)
        print(f"{r['ts']}  {','.join(r['genes']):28s}  {r['task'][:50]}")
    return 0

def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 1
    if a[0] == 'last':
        return cmd_last()
    if a[0] != 'add':
        print(__doc__); return 1
    rest = a[1:]
    task, trace, genes = '', '', []
    i = 0
    while i < len(rest):
        if rest[i] == '--task':
            i += 1; task = rest[i]
        elif rest[i] == '--trace':
            i += 1; trace = rest[i]
        else:
            genes.append(rest[i])
        i += 1
    if not genes:
        print("用法: gene_trace.py add <GENE_ID...> [--task 说明] [--trace path]"); return 1
    return cmd_add(genes, task, trace)

if __name__ == '__main__':
    sys.exit(main())
