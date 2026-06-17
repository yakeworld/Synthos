#!/usr/bin/env python3
"""AKNE 综合健康审计 — 替代零散检查脚本。一次运行覆盖16项指标。

用法: python3 akne-comprehensive-audit.py
输出: 结构化文本报告，标记通过/问题。
"""
import json, os, sqlite3, re
from collections import Counter

GRAPH_JSON = "/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/graph.json"
ROOT = "/media/yakeworld/sda2/academic_writer/yakeworld"

g = json.load(open(GRAPH_JSON))
nodes = g['nodes']
edges = g['edges']

results = {}
issues = []

# 1. 节点类型分布
types = {}
for n in nodes:
    t = n.get('type', 'unknown')
    types[t] = types.get(t, 0) + 1
results['node_types'] = types

# 2. 边类型分布
edge_types = {}
for e in edges:
    lt = e.get('link_type', 'unknown')
    edge_types[lt] = edge_types.get(lt, 0) + 1
results['edge_types'] = edge_types

# 3. 连通性
conn = set()
for e in edges:
    conn.add(e['source'])
    conn.add(e['target'])
all_names = set(n['name'] for n in nodes)
connected = conn.intersection(all_names)
pct = len(connected) / len(all_names) * 100 if all_names else 0
results['connectivity_pct'] = pct
if pct < 99:
    issues.append(f"连通率低于99%: {pct:.1f}%")

# 4. 孤立节点
isolated = [n for n in nodes if n['name'] not in conn]
iso_by_type = {}
for n in isolated:
    iso_by_type[n.get('type', 'unknown')] = iso_by_type.get(n.get('type', 'unknown'), 0) + 1
results['isolated_count'] = len(isolated)
results['isolated_by_type'] = iso_by_type
if isolated:
    issues.append(f"{len(isolated)}个孤立节点: {iso_by_type}")

# 5. 重名
names = [n['name'] for n in nodes]
dupes = {k: v for k, v in Counter(names).items() if v > 1}
results['duplicate_names'] = dupes
if dupes:
    issues.append(f"{len(dupes)}个重名: {dupes}")

# 6. 源文件覆盖
src_nodes = [n for n in nodes if n['type'] == 'source']
src_dir = os.path.join(ROOT, '.knowledge', 'sources')
disk_files = set()
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.md'):
            disk_files.add(os.path.relpath(os.path.join(root, f), ROOT))
graph_files = set(n['name'] for n in src_nodes)
missing_from_graph = disk_files - graph_files
missing_from_disk = graph_files - disk_files
results['source_coverage'] = {
    'disk_files': len(disk_files),
    'graph_nodes': len(graph_files),
    'missing_from_graph': len(missing_from_graph),
    'missing_from_disk': len(missing_from_disk),
}
if missing_from_graph:
    issues.append(f"{len(missing_from_graph)}个磁盘文件未入图")

# 7. 向量记录
vdb = os.path.join(ROOT, '.knowledge', 'vectors.db')
conn_db = sqlite3.connect(vdb)
vec_count = conn_db.execute('SELECT COUNT(*) FROM vectors').fetchone()[0]
conn_db.close()
results['vector_count'] = vec_count

# 8. Synthos论文孤立
papers = [n for n in nodes if n['type'] == 'synthos_paper']
paper_iso = [p['name'] for p in papers if p['name'] not in conn]
results['isolated_papers'] = len(paper_iso)
if paper_iso:
    issues.append(f"{len(paper_iso)}篇孤立论文")

# 9. Synthos技能孤立
skills = [n for n in nodes if n['type'] == 'synthos_skill']
skill_iso = [s['name'] for s in skills if s['name'] not in conn]
results['isolated_skills'] = len(skill_iso)
if skill_iso:
    issues.append(f"{len(skill_iso)}个孤立技能")

# 10. 自环边
self_loops = [e for e in edges if e['source'] == e['target']]
results['self_loops'] = len(self_loops)
if self_loops:
    loop_types = {}
    for e in self_loops:
        lt = e.get('link_type', 'unknown')
        loop_types[lt] = loop_types.get(lt, 0) + 1
    results['self_loop_types'] = loop_types
    issues.append(f"{len(self_loops)}条自环边")

# 11. 边格式
has_relation_only = sum(1 for e in edges if 'relation' in e and 'link_type' not in e)
has_link_type_only = sum(1 for e in edges if 'link_type' in e and 'relation' not in e)
results['edge_format'] = {
    'link_type_only': has_link_type_only,
    'relation_only': has_relation_only,
}
if has_relation_only > 0:
    issues.append(f"{has_relation_only}条边仍用relation字段")

# 12. 路径格式
dot_knowledge_paths = [n['name'] for n in nodes if '.knowledge/' in n.get('name', '')]
results['dot_knowledge_prefix_count'] = len(dot_knowledge_paths)
if dot_knowledge_paths:
    issues.append(f"{len(dot_knowledge_paths)}个节点使用.knowledge/前缀")

# 13. 元数据质量
nodes_no_metadata = [n for n in nodes if 'metadata' not in n or not n['metadata']]
results['nodes_no_metadata'] = len(nodes_no_metadata)
if nodes_no_metadata:
    issues.append(f"{len(nodes_no_metadata)}个节点无metadata")

# 14. Wiki污染
garbage_re = re.compile(r'^\s*\[.*\]\s*::')
garbage_found = []
for wf in ['wiki/index.md', 'wiki/log.md', os.path.join(ROOT, 'CATALOG.md')]:
    if os.path.exists(wf):
        content = open(wf, 'r', encoding='utf-8', errors='ignore').read()
        garbage = [l for l in content.split('\n') if garbage_re.match(l)]
        if garbage:
            garbage_found.append((wf, len(garbage)))
results['wiki_pollution'] = garbage_found
if garbage_found:
    issues.append(f"Wiki污染: {sum(c for _, c in garbage_found)}行")

# 15. Entity命名空间
entity_nodes = [n for n in nodes if n['type'] == 'entity']
wrong_ns = []
for n in entity_nodes:
    name = n['name']
    if '/' in name:
        first_seg = name.split('/')[0]
        if first_seg not in ('entities', 'wiki', 'concepts', 'CATALOG', 'catalog-new'):
            wrong_ns.append(name)
    else:
        if name not in ('CATALOG', 'catalog-new', 'MOC'):
            wrong_ns.append(name)
results['entity_wrong_namespace'] = len(wrong_ns)

# 16. 自环细分
sl_types = {}
for e in self_loops:
    t = e.get('link_type', 'unknown')
    sl_types[t] = sl_types.get(t, 0) + 1
results['self_loop_detail'] = sl_types

# ===== 输出报告 =====
print("=" * 60)
print("AKNE 综合健康审计")
print("=" * 60)
print(f"总节点: {len(nodes)}")
print(f"总边: {len(edges)}")
print(f"连通率: {pct:.1f}%")
print(f"孤立节点: {len(isolated)}")
print(f"重名: {len(dupes)}")
print(f"源文件覆盖: {len(disk_files)}磁盘 / {len(graph_files)}图")
print(f"向量记录: {vec_count}")
print(f"Synthos论文: {len(papers)}总, {len(paper_iso)}孤立")
print(f"Synthos技能: {len(skills)}总, {len(skill_iso)}孤立")
print(f"自环边: {len(self_loops)}")
print(f"边格式: {has_link_type_only} link_type, {has_relation_only} relation")
print(f"路径前缀: {len(dot_knowledge_paths)}个.knowledge/前缀")
print(f"无metadata: {len(nodes_no_metadata)}")
print(f"Entity命名空间异常: {len(wrong_ns)}")
if garbage_found:
    for p, c in garbage_found:
        print(f"Wiki污染: {p} = {c}行")
else:
    print("Wiki污染: 0 — OK")

print("\n" + "=" * 60)
if issues:
    print(f"发现问题: {len(issues)}")
    for i in issues:
        print(f"  ⚠ {i}")
else:
    print("健康状态: 全部通过 ✓")
print("=" * 60)

# 保存到文件
report_path = os.path.join(ROOT, '.knowledge', 'audit-report-latest.json')
with open(report_path, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n报告已保存: {report_path}")
