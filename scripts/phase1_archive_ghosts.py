#!/usr/bin/env python3
"""Phase 1: Pipeline_trace 强制持久化 + 幽灵论文归档"""
import json
import os

PAPERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'papers')
QUEUE_FILE = os.path.join(PAPERS_DIR, 'paper-queue.json')

def load_quality(paper_dir):
    final_path = os.path.join(paper_dir, '07-quality', 'final.json')
    if os.path.exists(final_path):
        with open(final_path) as f:
            return json.load(f)
    return None

def load_status(paper_dir):
    status_path = os.path.join(paper_dir, '07-quality', 'status.json')
    if os.path.exists(status_path):
        with open(status_path) as f:
            return json.load(f)
    return None

def generate_trace(paper_id, paper_dir, is_ghost=False, ghost_status=None):
    trace = {
        'paper_id': paper_id,
        'version': '1.0',
        'created_via': 'ad_hoc_ai_session',
        'discovered_at': 'phase1_auto_discovery' if is_ghost else 'existing',
        'pipeline_steps': [],
        'metadata': {
            'has_tex': os.path.exists(os.path.join(paper_dir, '01-manuscript', 'paper.tex')),
            'has_pdf': (os.path.exists(os.path.join(paper_dir, 'paper.pdf')) or
                       os.path.exists(os.path.join(paper_dir, '01-manuscript', 'paper.pdf')) or
                       os.path.exists(os.path.join(paper_dir, '02-submission', 'paper.pdf'))),
            'has_quality': os.path.exists(os.path.join(paper_dir, '07-quality', 'final.json')),
            'ghost_paper': is_ghost,
            'sections': {
                '01-manuscript': os.path.isdir(os.path.join(paper_dir, '01-manuscript')),
                '02-submission': os.path.isdir(os.path.join(paper_dir, '02-submission')),
                '03-code': os.path.isdir(os.path.join(paper_dir, '03-code')),
                '05-results': os.path.isdir(os.path.join(paper_dir, '05-results')),
                '06-references': os.path.isdir(os.path.join(paper_dir, '06-references')),
                '07-quality': os.path.isdir(os.path.join(paper_dir, '07-quality')),
            }
        }
    }
    if is_ghost and ghost_status:
        trace['metadata']['ghost_status'] = ghost_status

    trace_path = os.path.join(paper_dir, 'pipeline_trace.json')
    with open(trace_path, 'w') as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

def main():
    with open(QUEUE_FILE) as f:
        queue_data = json.load(f)
    existing_papers = queue_data.get('papers', [])
    existing_ids = set(p['paper_id'] for p in existing_papers)

    ghost_papers = []

    for item in sorted(os.listdir(PAPERS_DIR)):
        full_path = os.path.join(PAPERS_DIR, item)
        if not os.path.isdir(full_path):
            continue
        if not os.path.exists(os.path.join(full_path, '01-manuscript', 'paper.tex')):
            continue

        has_quality = os.path.exists(os.path.join(full_path, '07-quality', 'final.json'))
        has_status = os.path.exists(os.path.join(full_path, '07-quality', 'status.json'))
        has_pdf = (os.path.exists(os.path.join(full_path, 'paper.pdf')) or
                   os.path.exists(os.path.join(full_path, '01-manuscript', 'paper.pdf')) or
                   os.path.exists(os.path.join(full_path, '02-submission', 'paper.pdf')))
        paper_id = item

        if paper_id in existing_ids:
            # Already tracked - ensure pipeline_trace exists
            trace_path = os.path.join(full_path, 'pipeline_trace.json')
            if not os.path.exists(trace_path):
                generate_trace(paper_id, full_path)
            else:
                with open(trace_path) as f:
                    trace = json.load(f)
                trace['metadata']['ghost_paper'] = False
                trace['metadata']['sections'] = {
                    '01-manuscript': os.path.isdir(os.path.join(full_path, '01-manuscript')),
                    '02-submission': os.path.isdir(os.path.join(full_path, '02-submission')),
                    '03-code': os.path.isdir(os.path.join(full_path, '03-code')),
                    '05-results': os.path.isdir(os.path.join(full_path, '05-results')),
                    '06-references': os.path.isdir(os.path.join(full_path, '06-references')),
                    '07-quality': os.path.isdir(os.path.join(full_path, '07-quality')),
                }
                with open(trace_path, 'w') as f:
                    json.dump(trace, f, indent=2, ensure_ascii=False)
        else:
            # Ghost paper
            quality = load_quality(full_path)
            if quality and quality.get('overall_pass', False):
                ghost_status = 'completed_no_trace'
            elif has_quality and has_status:
                st = load_status(full_path)
                st_val = st.get('status', st.get('gate_status', 'unknown')) if st else 'unknown'
                ghost_status = 'pending_review' if 'pending' in str(st_val).lower() else 'completed_no_trace'
            else:
                ghost_status = 'incomplete'

            ghost_papers.append({'id': paper_id, 'ghost_status': ghost_status, 'has_quality': has_quality, 'has_pdf': has_pdf})
            generate_trace(paper_id, full_path, is_ghost=True, ghost_status=ghost_status)

    # Update queue: add ghost papers, fix notes for missing dirs
    new_queue_papers = []
    for p in existing_papers:
        full_path = os.path.join(PAPERS_DIR, p['paper_id'])
        notes = p.get('notes', '')
        if isinstance(notes, dict):
            notes = json.dumps(notes, ensure_ascii=False)
        if not os.path.exists(full_path):
            notes = (notes + ' | DIRECTORY_MISSING') if notes else 'DIRECTORY_MISSING'
            new_queue_papers.append({**p, 'notes': notes})
        else:
            new_queue_papers.append(p)

    for ghost in ghost_papers:
        new_queue_papers.append({
            'paper_id': ghost['id'],
            'status': ghost['ghost_status'],
            'reason': 'ghost_paper_autodiscovered',
            'quality_score': 0.0,
            'gate_status': 'UNKNOWN',
            'last_updated': 'phase1',
            'notes': f'Ghost paper discovered in Phase 1. Status: {ghost["ghost_status"]}',
        })

    queue_data['papers'] = new_queue_papers
    queue_data['metadata'] = {
        'version': '2.0',
        'last_updated': 'phase1_archive_ghosts',
        'total_papers': len(new_queue_papers),
        'ghost_papers_added': len(ghost_papers),
    }

    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue_data, f, indent=2, ensure_ascii=False)

    status_counts = {}
    for p in new_queue_papers:
        s = p.get('status', 'unknown')
        status_counts[s] = status_counts.get(s, 0) + 1

    print("Phase 1 Complete:")
    print(f"  Ghost papers discovered: {len(ghost_papers)}")
    print(f"  Total tracked: {len(new_queue_papers)}")
    print(f"  Status distribution:")
    for s, c in sorted(status_counts.items()):
        print(f"    {s}: {c}")

if __name__ == '__main__':
    main()
