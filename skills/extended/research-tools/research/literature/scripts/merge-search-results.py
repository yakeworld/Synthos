#!/usr/bin/env python3
"""
合并多轮搜索结果并去重（按 DOI）。

用法: python3 merge-search-results.py [input_dir] [output_file]

输入: glob.glob(f"{input_dir}/search_*.json") — 每轮检索结果
输出: JSON 文件，包含所有唯一论文

示例:
    python3 merge-search-results.py /tmp "all_papers.json"
    python3 merge-search-results.py
"""

import json
import sys
import glob
import os


def merge_search_results(input_dir=".", output_file="all_papers.json"):
    """合并多轮搜索结果，按 DOI 去重。

    去重策略:
        - 优先使用 paper['doi']
        - 兜底使用 paper['provenance']（包含 source= 前缀）
        - 空 DOI 的论文也会保留（按 provenance 去重）
    """
    pattern = os.path.join(input_dir, "search_*.json")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"No search_*.json files found in {input_dir}")
        return []
    
    all_papers = []
    seen = set()
    source_counts = {}
    
    for f in files:
        try:
            data = json.load(open(f))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Skipping {f}: {e}")
            continue
        
        source = os.path.basename(f).replace('search_', '').replace('.json', '')
        
        for p in data.get('papers', []):
            # 去重键: 优先 DOI，其次 provenance
            doi = p.get('doi', '')
            provenance = p.get('provenance', '')
            
            if doi:
                key = f"doi:{doi}"
            elif provenance:
                key = f"prov:{provenance}"
            else:
                # 无 DOI 无 provenance，按标题去重
                key = f"title:{p.get('title', '').lower()}"
            
            if key not in seen:
                seen.add(key)
                # 标记来源
                p['_source'] = source
                all_papers.append(p)
                
                # 统计源分布
                actual_source = p.get('source', source)
                source_counts[actual_source] = source_counts.get(actual_source, 0) + 1
    
    # 保存结果
    with open(output_file, 'w') as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)
    
    print(f"Merged {len(files)} search files")
    print(f"Total unique papers: {len(all_papers)}")
    print(f"Sources: {json.dumps(source_counts, indent=2)}")
    print(f"Saved to: {output_file}")
    
    return all_papers


if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "all_papers.json"
    merge_search_results(input_dir, output_file)