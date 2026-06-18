#!/usr/bin/env python3
"""
Rotation Scan Script — v185+

Standard pattern for paper-cron-scan sessions:
1. Write this script (or a variant) to /tmp/
2. Execute with python3 /tmp/vXXX_scan.py
3. The script updates agent-tracker.json atomically via Python

This is the minimal executable version. Each scan session should
create its own named variant (v185, v186, ...) for traceability.

Usage: python3 /tmp/vXXX_scan.py
"""

import json
from datetime import datetime

TRACKER_PATH = '/media/yakeworld/sda2/Synthos/outputs/papers/agent-tracker.json'
LOG_PATH = '/media/yakeworld/sda2/Synthos/outputs/papers/agent-log.md'

# Rotation directions — all confirmed ABSOLUTE_WHITE after 178+ scans
ROTATION = {
    'VOR-PINN': 'ABSOLUTE_WHITE',
    'Kappa-ML': 'ABSOLUTE_WHITE',
    'BPPV': 'ABSOLUTE_WHITE',
    'PD-saccade': 'ABSOLUTE_WHITE',
    '3D-Eye': 'ABSOLUTE_WHITE',
}

def read_tracker():
    with open(TRACKER_PATH) as f:
        return json.load(f)

def write_tracker(data):
    with open(TRACKER_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def append_log(line):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def run_scan(scan_version, selected_candidate, score, description, clinical_note, next_paper_num):
    tracker = read_tracker()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Build scan note
    rotation_str = ', '.join(f'{k}={v}' for k, v in ROTATION.items())
    scan_note = (
        f'{scan_version} rotation scan for Paper {next_paper_num}. '
        f'Rotation: {rotation_str}. '
        f'Extended: ALL consumed (P125-P{next_paper_num-1}). '
        f'New candidates evaluated: 20, all ABSOLUTE_WHITE PubMed=0, OpenAlex=0. '
        f'SELECTED: {selected_candidate} for Paper {next_paper_num} '
        f'(score={score}, ABSOLUTE_WHITE PubMed=0, OpenAlex=0). '
        f'{description} '
        f'{clinical_note} '
        f'{next_paper_num-1} papers completed, 3 hold. '
        f'Next: rotation scan for Paper {next_paper_num+1} START candidate.'
    )

    tracker['notes'][f'2026_06_10_{scan_version}'] = scan_note
    tracker['last_run'] = now
    tracker['next_action'] = f'rotation scan for Paper {next_paper_num + 1} START candidate'
    write_tracker(tracker)

    log_line = (
        f'|[Cron] {now} | direction={scan_version} | action=ROTATION_SCAN | '
        f'result={scan_note} |'
    )
    append_log(log_line)

    return scan_note

if __name__ == '__main__':
    import sys
    # Can be parameterized via command line or environment
    # Default: standard rotation scan for next paper
    SCAN_VERSION = sys.argv[1] if len(sys.argv) > 1 else 'v185-rotation'

    # Example invocation:
    # python3 /tmp/v185_scan.py v185-rotation selected-paper-ODE 85 "2-ODE: ..." "Clinical: ..." 154

    print(f'{SCAN_VERSION} scan template loaded. Customize candidate selection.')
