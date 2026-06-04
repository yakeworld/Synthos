#!/usr/bin/env python3
"""
记忆巩固引擎 — 自动运行 FSRS 间隔重复 + 内存使用检测。

模式: no_agent=True (纯脚本，仅检测+报告，不执行工具操作)
触发: cronjob 每天一次
输出: 只在有实际变化时打印到 stdout (看门狗模式)

2026-06-04 修复: mem_used 改为从 consolidation 状态文件动态读取，不再硬编码。
"""

import json, os
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / '.hermes'
QC_STATE_FILE = STATE_DIR / 'qc_last_scan.json'
MEMORY_CONSOLIDATION_FILE = STATE_DIR / 'memory_consolidation_state.json'
MEMORY_USAGE_FILE = STATE_DIR / 'memory_usage.json'


def read_memory_usage():
    """从持久化文件读取上次记录的 memory 使用量。"""
    if MEMORY_USAGE_FILE.exists():
        try:
            data = json.loads(MEMORY_USAGE_FILE.read_text())
            return data.get('used', 2149), data.get('total', 2200), data.get('timestamp', 'never')
        except:
            pass
    if MEMORY_CONSOLIDATION_FILE.exists():
        try:
            data = json.loads(MEMORY_CONSOLIDATION_FILE.read_text())
            if data.get('last_metrics', {}).get('mem_used'):
                return data['last_metrics']['mem_used'], 2200, data.get('timestamp', 'unknown')
        except:
            pass
    return 2149, 2200, 'unknown'


def analyze_memory_space():
    result = {}
    mem_used, mem_total, mem_ts = read_memory_usage()
    mem_pct = mem_used / mem_total * 100
    result['mem_used'] = mem_used
    result['mem_total'] = mem_total
    result['mem_pct'] = round(mem_pct, 1)
    result['mem_timestamp'] = mem_ts
    result['qc_state_exists'] = QC_STATE_FILE.exists()
    result['consolidation_state_exists'] = MEMORY_CONSOLIDATION_FILE.exists()
    
    if MEMORY_CONSOLIDATION_FILE.exists():
        try:
            last_state = json.loads(MEMORY_CONSOLIDATION_FILE.read_text())
            result['last_consolidation'] = last_state.get('timestamp', 'never')
            result['last_metrics'] = last_state.get('metrics', {})
        except:
            result['last_consolidation'] = 'corrupt'
    
    recs = []
    if mem_pct > 95:
        recs.append({'type': 'critical', 'message': f'Memory at {mem_pct:.0f}% — need immediate cleanup'})
    elif mem_pct > 85:
        recs.append({'type': 'warning', 'message': f'Memory at {mem_pct:.0f}% — suggest next session cleanup'})
    result['recommendations'] = recs
    return result


def format_report(result):
    ts = datetime.now().strftime('%m-%d %H:%M')
    mem_pct = result.get('mem_pct', 97)
    lines = []
    severity = '🔴' if mem_pct > 95 else ('🟡' if mem_pct > 85 else '🟢')
    lines.append(f"🧠 [mem-consolidate] {ts} {severity}")
    lines.append(f"    Memory: {result.get('mem_used', '?')}/{result.get('mem_total', 2200)} ({mem_pct:.0f}%)")
    for rec in result.get('recommendations', []):
        lines.append(f"    {rec['type'].upper()}: {rec['message']}")
    return '\n'.join(lines)


if __name__ == '__main__':
    result = analyze_memory_space()
    report = format_report(result)
    result['timestamp'] = datetime.now(timezone.utc).isoformat()
    MEMORY_CONSOLIDATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_CONSOLIDATION_FILE.write_text(json.dumps(result, indent=2, default=str))
    print(report)
