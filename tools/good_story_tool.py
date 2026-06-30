#!/usr/bin/env python3
"""
好故事打磨工具 — 为顶刊准备论文故事包
用法: python3 good_story_tool.py <paper_dir> [target_journal]
"""

import json
import os
import sys


def load_state(paper_dir):
    """加载论文状态文件"""
    state_file = os.path.join(paper_dir, 'state.json')
    if not os.path.exists(state_file):
        raise FileNotFoundError(f"state.json not found in {paper_dir}")
    with open(state_file, 'r') as f:
        return json.load(f)


def extract_story_elements(state):
    """从state.json提取故事元素"""
    title = state.get('title', 'NO_TITLE')
    quality = state.get('quality_score', 0)
    gates = state.get('gates_result', {}).get('gates', [])
    changes = state.get('changes', [])
    checks = state.get('checks', {})
    
    # 提取核心数据
    experiment = state.get('experiment_k6', state.get('experiment_results', {}))
    
    return {
        'title': title,
        'quality_score': quality,
        'gate_count': len([g for g in gates if g.get('status') == 'PASS']),
        'total_gates': len(gates),
        'changes_count': len(changes),
        'experiment_data': experiment,
        'checks': checks
    }


def generate_story_package(state):
    """生成故事包"""
    elements = extract_story_elements(state)
    
    story = {
        'one_line_summary': f"{elements['title']} — Quality: {elements['quality_score']}",
        'hook': f"The fundamental challenge in clinical AI is balancing accuracy and safety.",
        'gap': "Existing methods treat these as competing objectives.",
        'insight': "We show they can be structurally decoupled.",
        'method': "Cascade architecture with three-way classification.",
        'results': elements.get('experiment_data', {}),
        'implication': "Structural innovation can simultaneously achieve safety and efficiency.",
        'journal_fit': 'Needs target journal specification for accurate matching.',
        'pre_mortem': [
            'Reviewer 1: "Why not just use ensemble methods?"',
            'Reviewer 2: "Where are the validation results?"',
            'Reviewer 3: "What is the clinical significance?"'
        ]
    }
    
    return story


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 good_story_tool.py <paper_dir> [target_journal]")
        sys.exit(1)
    
    paper_dir = sys.argv[1]
    target_journal = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        state = load_state(paper_dir)
        story = generate_story_package(state)
        print(json.dumps(story, indent=2, ensure_ascii=False))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
