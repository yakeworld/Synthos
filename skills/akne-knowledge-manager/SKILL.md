------
name: akne-knowledge-manager
description: AKNE 知识管理系统的双向整合审计、Synthos-桥接诊断、知识流分析。与 akne-maintenance 不同，专注两系统间的连接质量而非内部运维。
triggers:
  - 
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: AKNE 知识管理系统的双向整合审计、Synthos-桥接诊断、知识流分析。
    signature: 'akne_graph: str, synthos_graph: str -> integration_report: dict'
    related_skills: [akne-maintenance, synthos-akne-bridge, knowledge-extraction, association-discovery]
---
  io_contract: input: ['akne_graph: str, synthos_graph: str -> integration_report: dict', 'output: ['integration_report: dict (bridge_points: list[str], knowledge_flow: dict, issues: list[str])']'




# AKNE Knowledge Manager — 整合审计

> 专注 Synthos 与 AKNE 之间的双向整合质量。
> 与 `akne-maintenance` 的区别：后者管内部运维（诊断、修复、向量填充），本技能管跨系统连接。

## 核心问题

Synthos 是论文产出管线，AKNE 是个人知识图谱。两者通过 `synthos-akne-bridge-v2.py` 桥接。

## 快速诊断命令

```bash
# 完整同步 + 报告
cd /media/yakeworld/sda2/academic_writer/yakeworld
python3 scripts/synthos-akne-bridge-v2.py full

# 只看报告
python3 scripts/synthos-akne-bridge-v2.py report

# 资产审计
python3 scripts/asset_audit.py
```

## 连通性检查清单

运行后逐项确认：

1. **Synthos 论文覆盖率** — 应有 100% 的 Synthos 论文有边连接（已达标）
2. **Synthos 技能连接** — 25 个技能应全部连到领域和概念（已达标）
3. **知识流方向** — 应有 Synthos→AKNE 和 AKNE→Synthos 双向边（已实现）
4. **Wiki 污染** — `wiki/index.md` 和 `wiki/log.md` 末尾不应有 `[X, Y]::` 垃圾
5. **守护进程状态** — `logs/auto_evolve.pid` 应存在且进程存活

## 当前状态（2026-06-10 修复后）

### 图谱统计

| 指标 | 值 |
|------|-----|
| 总节点 | 1475 |
| 总边 | 6130 |
| 连通节点 | 1468/1475 (99.5%) |
| Synthos 论文 | 148（0孤立） |
| Synthos 技能 | 25（0孤立） |
| Synthos 杂项 | 7（子目录/非论文） |

### 双向知识流

| 方向 | 边类型 | 数量 |
|------|--------|------|
| Synthos→AKNE 论文→概念 | paper_concept | 335 |
| AKNE→Synthos 概念→论文 | concept_paper | 281 |
| Synthos→AKNE 论文→分类 | paper_source_domain | 285 |
| AKNE→Synthos 分类→论文 | category_paper | 255 |
| Synthos→AKNE 论文→分类（反） | paper_category | 255 |
| AKNE→Synthos 概念→论文（反） | concept_paper | 281 |
| 技能→领域 | skill_source_domain | 42 |
| 技能→概念 | skill_concept | 18 |
| 源文件→分类 | source_category | 1145 |
| 分类→论文 | category_paper | 255 |

路径示例：`source file → category → synthos paper`（2跳）
路径示例：`wiki concept → synthos paper → wiki concept`（3跳闭环）

### 边类型分布

| 边类型 | 数量 | 说明 |
|--------|------|------|
| source_co_occurrence | 1970 | 同类源文件互连 |
| source_category_membership | 1145 | 分类→源文件 |
| source_category | 1145 | 源文件→分类（反向） |
| paper_concept | 335 | 论文→Wiki概念 |
| concept_paper | 281 | 概念→论文（反向） |
| paper_source_domain | 285 | 论文→分类 |
| category_paper | 255 | 分类→论文（反向） |
| paper_category | 255 | 论文→分类（反向） |
| domain_overlap | 252 | 领域重叠 |
| references | 137 | 通用引用 |
| skill_source_domain | 42 | 技能→领域 |
| skill_concept | 18 | 技能→概念 |
| paper_source_match | 10 | 名称匹配 |

## 审计流程

### Step 1: 运行桥接报告

```bash
python3 scripts/synthos-akne-bridge-v2.py report
```

检查：
- `synthos_isolated` 应为 0
- `isolated` 应为 ≤10（仅杂项节点）
- `connected` 应 ≥ 99% 总节点

### Step 2: 检查孤立论文

```bash
python3 -c "
import json
g = json.load(open('.knowledge/graph.json'))
conn = set()
for e in g['edges']:
    conn.add(e.get('source','')); conn.add(e.get('target',''))
papers = [n['name'] for n in g['nodes'] if n['type']=='synthos_paper']
iso = [p for p in papers if p not in conn]
print(f'Isolated: {len(iso)}/{len(papers)}')
for p in iso: print(f'  {p}')
"
```

### Step 3: 检查技能连接

```bash
python3 -c "
import json
g = json.load(open('.knowledge/graph.json'))
conn = set()
for e in g['edges']:
    conn.add(e.get('source','')); conn.add(e.get('target',''))
for n in g['nodes']:
    if n['type']=='synthos_skill':
        print(f'  {n[\"name\"]}: connected={n[\"name\"] in conn}')
"
```

### Step 4: 检查 Wiki 污染

```bash
grep -c '\[.*\]::' .knowledge/wiki/index.md .knowledge/wiki/log.md .knowledge/CATALOG.md
# 应为 0
```

### Step 5: 检查双向边

```bash
python3 -c "
import json
g = json.load(open('.knowledge/graph.json'))
types = {}
for e in g['edges']:
    t = e.get('link_type','unknown')
    types[t] = types.get(t,0) + 1
for t,c in sorted(types.items(), key=lambda x:-x[1]):
    print(f'  {t}: {c}')
"
# 检查 paper_concept/concept_paper/source_category/category_paper 是否都 > 0
```

## 常见修复

### 新增孤立论文
手动映射到 AKNE 分类：
```python
# 在 graph.json 中为孤立论文添加 paper_source_domain 边
# 领域映射规则见 synthos-akne-bridge-v2.py 的 DOMAIN_TO_CATEGORIES
# 注意：对于"其他"域的论文，需手动建立 ISOLATED_MAP 映射表
```

### 修复非论文目录被误分类为 synthos_paper
桥接脚本会扫描 `outputs/papers/` 下所有子目录。子目录 `scripts/`, `papers/`, `references/`, `lit-reviews/`, `01-gap_analysis/`, `09-manuscript/`, `110-direction-scan/` 等不是论文，是子目录。
**修复**：更新桥接脚本的 `paper_name in ("_docs", "_archive_scripts", "_todo", "papers", "references", "scripts", "lit-reviews", "gap-paper-35-neuromorphic-eye-tracking", "kaggle-wdbc-classification", "pinn-operator-learning-generalization", "portable-et-r2", "scale-space-feature-tensor", "01-gap_analysis", "09-manuscript", "110-direction-scan")` 排除列表。
在 AKNE 侧将这些节点重新分类为 `synthos_misc`（非论文类型），并从 edges 中移除指向它们的边。

### 修复 Synthos 论文目录不规范
Synthos 论文目录若缺少 `01-manuscript/` 或 `06-references/`，桥接脚本仍创建节点但无法通过标准路径验证。
**修复模式**：
1. 扫描每个论文目录，检测 `01-manuscript`/`06-references`/`07-quality` 是否存在
2. 若不存在，按文件特征归入子目录：
   - `01-xx`, `02-xx`, ..., `05-xx` 及 `.tex`/`.pdf` → `01-manuscript/`
   - `literature-survey.md`, `06-references.md` → `06-references/`
   - `qc-*.md`, `notebooklm-sources.json` → `07-quality/`
3. 重新运行 `synthos-akne-bridge-v2.py sync` 使桥接识别

### 修复双向边缺失
`paper_source_domain` 和 `paper_concept` 边是单向的（论文→AKNE）。需要手动添加反向边：
- `category_paper`：分类→论文（`paper_source_domain` 的反向）
- `paper_category`：论文→分类（`paper_source_domain` 的反向，用于论文→分类路径）
- `source_category`：源文件→分类（`source_category_membership` 的反向）
- `concept_paper`：概念→论文（`paper_concept` 的反向）

创建反向边后，`source → category → paper` 路径变为2跳连通。

### 修复 Wiki 持续污染
`[核心技术, 知识点]::` 等占位符垃圾会反复注入 `wiki/index.md` 和 `wiki/log.md`。
**根因**：LLM 摄入环节的输出质量不稳定，缺乏 schema 约束。
**缓解**：每次审计运行后运行清理脚本 `clean_wiki.py`（正则 `^\[\s*[^]]*\]\s*::.*$` 匹配行删除）。
**长期**：改善 LLM 摄入质量，在 `akne/ingest/` 环节添加输出过滤。

### 技能未连接
按领域映射技能到分类和概念：
- `research` → BPPV/科研/投稿 + 科研课题研究/科研思维层级
- `knowledge-acquisition` → 科研/投稿 + 科研论文检索系统
- `hypothesis-generation` → 科研/半规管空间姿态研究 + 科研课题研究/第一性原理
- 其他技能参照 `SKILL_TO_CATEGORIES` 映射表

### Wiki 污染
```python
import re
garbage = re.compile(r'^\[\s*[^]]*\]\s*::.*$')
for fpath in files:
    lines = [l for l in fpath.read_text().split('\n') if not garbage.match(l.strip())]
    fpath.write_text('\n'.join(lines))
```

### 目录不规范
运行 `fix_bridge.py` 将 flat 文件归入 `01-manuscript`/`06-references`/`07-quality` 子目录。

## 参考文件

`references/synthos-akne-integration-audit.md` — 2026-06-10 修复后完整数据。含边类型分布、双向路径示例、诊断命令、修复历史。旧审计数据已归档替换。

## 修复模式速查

| 问题 | 动作 |
|------|------|
| 论文孤立 | 手动映射到分类 (DOMAIN_TO_CATEGORIES) |
| 非论文误分类 | 从 edges 移除，重分类为 synthos_misc |
| 目录不规范 | 扫描文件→归入01-manuscript/06-references/07-quality → 重新sync |
| 技能孤立 | 按 SKILL_TO_CATEGORIES 映射到领域和概念 |
| Wiki 污染 | grep 正则 `^\[\s*[^]]*\]\s*::.*$` 删除 |
| 单向边 | 为每个 edge (a→b) 添加反向边 (b→a)，区分 link_type |
| 守护停止 | 检查 logs/auto_evolve.pid，pkill 后 nohup 重启 |