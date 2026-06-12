------
name: akne-maintenance
description: 维护个人知识管理系统AKNE — 图谱诊断、修复、向量填充、源文件覆盖、Wiki清理、自动进化守护。覆盖AKNE仓库的完整运维生命周期。
triggers:
  - 
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: 维护个人知识管理系统AKNE — 图谱诊断、修复、向量填充、源文件覆盖、Wiki清理、自动进化守护。
    signature: 'akne_state: str -> maintenance_report: dict'
    related_skills: [akne-knowledge-manager, synthos-akne-bridge, knowledge-extraction, knowledge-acquisition]
---
  io_contract: input: ['akne_state: str -> maintenance_report: dict', 'output: ['maintenance_report: dict (node_counts: int, edge_counts: int, health_score: float, issues: list[str])']']




# AKNE Maintenance (个人知识管理系统维护)

> AKNE (Adaptive Knowledge Network Engine) 是个人知识管理系统
> 运行在 `/media/yakeworld/sda2/academic_writer/yakeworld/`
> 核心：`.knowledge/` 目录 + `akne/` Python引擎 + `scripts/` 运维

## 架构概览

```
.knowledge/
├── graph.json        # 知识图谱（~1475节点, ~6130边）
├── vectors.db        # SQLite向量数据库（~533记录）
├── sources/          # 1145篇Markdown源文件（24分类）
├── wiki/             # Obsidian风格Wiki
│   ├── concepts/     # 18个概念
│   ├── entities/     # 7个实体
│   └── projects/     # 项目条目（含Synthos集成）
├── plan/             # 5阶段实施计划
└── schema/           # 数据模式（空）

akne/                 # Python引擎
├── ingest/           # 文件采集+分块
├── embed/            # 向量嵌入（sentence-transformers）
├── graph/            # 知识图谱（NetworkX）
├── reason/           # 推理引擎
├── sync/             # Obsidian同步
└── verify/           # 完整性检查
```

## 运维脚本

### 1. 诊断 — `akne-optimize.py diagnose`

```bash
python3 ~/akne/scripts/akne-optimize.py diagnose
```

输出 JSON 报告，包含：
- 图谱：节点数、边数、孤立节点数、边格式分布
- 向量：记录数、文件大小
- 源文件：总数、在图谱中的数量、覆盖率
- Wiki：占位符污染行数

### 2. 修复 — `akne-optimize.py fix`

```bash
python3 ~/akne/scripts/akne-optimize.py fix
```

依次执行：
1. 统一边格式（`relation` → `link_type`，裸 `weight` → `link_type: domain_overlap`）
2. 去重（相同 source+target+link_type 的边）
3. 填充源文件节点（所有未在图谱中的源文件创建 `source` 类型节点）
4. 修复孤立论文（为每个孤立Synthos论文创建到AKNE源文件的边）

### 3. 填充向量 — `akne-optimize.py fill-vectors`

```bash
python3 ~/akne/scripts/akne-optimize.py fill-vectors
```

为源文件创建向量记录（不加载GPU模型，仅结构填充）。实际嵌入需要 sentence-transformers + GPU。

### 4. 桥接同步 — `synthos-akne-bridge-v2.py sync`

```bash
python3 ~/akne/scripts/synthos-akne-bridge-v2.py sync
```

增量同步 Synthos 论文/技能到 AKNE 图谱：
- 论文 → 源文件分类边（domain映射）
- 论文 → Wiki概念边（名称重叠）
- 技能 → 概念节点
- 自动统一边格式
- 记录变更到 `logs/bridge-log.jsonl`

### 5. 查询 — `akne-synthos-query.py`

```bash
python3 ~/akne/scripts/akne-synthos-query.py "BPPV"
python3 ~/akne/scripts/akne-synthos-query.py --domain "前庭生理"
python3 ~/akne/scripts/akne-synthos-query.py --list-domains
```

## 维护流程

### 健康检查（每次维护前）

```bash
# 快速诊断
python3 ~/akne/scripts/akne-optimize.py diagnose

# 检查关键指标
# 1. 图谱连通性 > 95%
# 2. 源文件覆盖率 100%
# 3. Wiki占位符污染 0
# 4. 向量记录 > 200
# 5. Synthos论文孤立 < 10%
```

### 修复流程（发现问题时）

```bash
# 1. 修复边格式和去重
python3 ~/akne/scripts/akne-optimize.py fix

# 2. 检查是否还需要填充
# 如果源文件覆盖率 < 100%
python3 ~/akne/scripts/akne-optimize.py fill-vectors

# 3. 重新桥接Synthos
python3 ~/akne/scripts/synthos-akne-bridge-v2.py sync

# 4. 再次诊断确认
python3 ~/akne/scripts/akne-optimize.py diagnose
```

### 自动进化

```bash
# 启动守护进程（每3600秒循环）
bash ~/akne/scripts/auto_evolve.sh

# 查看状态
cat ~/akne/logs/auto_evolve.pid
cat ~/akne/logs/auto_evolve.log | tail -20

# 停止
kill $(cat ~/akne/logs/auto_evolve.pid) 2>/dev/null || true
rm ~/akne/logs/auto_evolve.pid
```

自动进化循环执行：
1. 资产审计 (`asset_batch_tag.py`)
2. 资产审计摘要 (`asset_audit.py`)
3. AKNE优化 (`akne-optimize.py fix`)
4. Synthos桥接 (`synthos-akne-bridge-v2.py sync`)
5. 报告生成 (`synthos-akne-bridge-v2.py report`)

## 图谱结构规范

### 节点类型

| 类型 | 说明 | 数量 |
|------|------|------|
| `entity` | 疾病、人物、工具 | 126 |
| `source` | 源文件 | 1145 |
| `source_category` | 源文件分类hub | 24 |
| `synthos_paper` | Synthos论文 | 148 |
| `synthos_skill` | Synthos技能 | 25 |
| `synthos_misc` | 子目录/杂项（非论文） | 7 |

### 边类型

| 类型 | 说明 | 方向 | 数量 |
|------|------|------|------|
| `source_category_membership` | 分类→源文件 | cat→src | 1145 |
| `source_category` | 源文件→分类 | src→cat | 1145 |
| `source_co_occurrence` | 同类源文件互连 | src→src | 1970 |
| `paper_source_domain` | 论文→源文件分类 | paper→cat | 285 |
| `paper_category` | 论文→分类（反向） | paper→cat | 255 |
| `category_paper` | 分类→论文（反向） | cat→paper | 255 |
| `paper_concept` | 论文→Wiki概念 | paper→concept | 335 |
| `concept_paper` | 概念→论文（反向） | concept→paper | 281 |
| `domain_overlap` | 领域重叠 | paper↔paper | 252 |
| `references` | 通用引用 | various | 137 |
| `skill_source_domain` | 技能→领域 | skill→cat | 42 |
| `skill_concept` | 技能→概念 | skill→concept | 18 |
| `paper_source_match` | 名称匹配 | paper→src | 10 |

总计：6130 条边，1475 个节点。

### 连通性设计原则

- **源文件不直连**：所有源文件通过 `source_category` 节点连接，避免 O(n²) 边爆炸
- **双向路径**：`source → category → paper` 和 `paper → concept ↔ concept → paper` 形成双向知识流
- **论文→分类映射**：根据论文名称推断领域，映射到 1-2 个 AKNE 源文件分类
- **论文→概念映射**：基于名称重叠
- **Synthos 技能**：每个技能连到 2-3 个源文件分类 + 2-3 个 Wiki 概念

## 已发现陷阱

### 1. Wiki 占位符污染

AKNE 源文件中的 `[创新点, 核心技术, 知识点]:: 创新点, 核心技术, 知识点` 占位行会污染内容。BPPV wiki 曾出现 57 行污染（29%）。

**检测**:
```bash
grep -c "\[创新点, 核心技术, 知识点\]:: 创新点, 核心技术, 知识点" file.md
```

**修复**: 删除所有包含该模式的行。

### 2. 边格式不一致

旧图谱边有 `relation` 字段，新桥接使用 `link_type` 字段。混用导致查询结果不可预测。

**修复**: 每次同步时统一格式：
```python
if "relation" in edge and "link_type" not in edge:
    edge["link_type"] = edge.pop("relation")
if "link_type" not in edge:
    edge["link_type"] = "unknown"
```

### 3. 源文件孤立

如果源文件直接建节点但没有 category 中间层，所有源文件都会孤立（无边连接）。

**修复**: 先创建 `sources/分类名` 节点，再建 `分类→文件` 边，最后建同类文件互连边（限制每个文件最多7个）。

### 4. 向量空洞

vectors.db 初始可能只有 33 条记录（1145篇源文件）。填充后也只有结构记录（无实际 embedding），因为 GPU 模型未加载。

**修复**: `fill_vectors()` 仅做结构填充。实际嵌入需要 sentence-transformers 模型和 GPU。

### 5. 同步历史丢失

没有 bridge-log.jsonl 时，无法追溯每次同步变更。

**修复**: 每次同步记录到 `logs/bridge-log.jsonl`。

### 6. Synthos 论文目录不规范

`outputs/papers/` 中约 20% 目录缺少 `01-manuscript`/`06-references`/`07-quality` 子目录，导致桥接脚本可能跳过或误分类。

**修复流程**:
```python
# 用 fix_bridge.py 扫描并规范化
python3 /tmp/fix_bridge.py
# 或直接创建子目录
mkdir -p /path/to/paper/{01-manuscript,06-references,07-quality}
# 将 flat 文件移入对应子目录（按内容分类）
mv paper.tex 01-manuscript/
mv literature-survey.md 06-references/
mv qc-d8-refs.md 07-quality/
```

**注意**: 桥接脚本 `synthos-akne-bridge-v2.py` 已更新跳过非论文目录：`_docs`, `_archive_scripts`, `_todo`, `papers`, `references`, `scripts`, `lit-reviews`, `gap-paper-35-neuromorphic-eye-tracking`, `kaggle-wdbc-classification`, `pinn-operator-learning-generalization`, `portable-et-r2`, `scale-space-feature-tensor`, `01-gap_analysis`, `09-manuscript`, `110-direction-scan`。这些目录在 AKNE 侧被重新分类为 `synthos_misc` 节点。

### 7. Wiki 占位符污染复发

`[核心技术, 知识点]:: 核心技术, 知识点` 模式在 `wiki/index.md` 和 `wiki/log.md` 中反复出现。

**清理脚本**:
```python
import re
garbage = re.compile(r'^\[\s*[^]]*\]\s*::.*$')
for fpath in [wiki_dir/'index.md', wiki_dir/'log.md', ROOT/'CATALOG.md']:
    lines = [l for l in fpath.read_text().split('\n') if not garbage.match(l.strip())]
    fpath.write_text('\n'.join(lines))
```

**根因**: LLM 摄入环节输出的占位符格式垃圾。需要在摄入端增加 schema 验证门控。

## 质量目标

| 指标 | 当前值 |
|------|--------|
| 图谱连通性 | 99.5% (1468/1475) |
| 源文件覆盖率 | 100% (1145/1145) |
| Wiki占位符污染 | 0行 |
| 边格式统一 | 100% link_type |
| 向量记录 | 533 (45%覆盖率) |
| Synthos论文孤立 | 0 (148/148) |
| Synthos技能孤立 | 0 (25/25) |
| 总边数 | 6130 |

## 与 Synthos 的关系

AKNE 是 Synthos 的知识基础。Synthos 的论文产出通过桥接注入 AKNE，AKNE 的查询能力服务 Synthos 写作。

```
Synthos (论文管线) → AKNE (知识图谱)
     │                      │
     ├─ 论文注入 ──────────► 节点+边
     ├─ 技能索引 ──────────► 概念节点
     ├─ 领域重叠 ──────────► 跨系统边
     │                      │
     ◄─ 反向查询 ──────────  实体/概念
     ◄─ 知识检索 ──────────  源文件
```

## 参考文件

| 路径 | 用途 |
|------|------|
| `references/operations-reference.md` | 运维操作速查 — 日常检查、修复、守护进程、常见问题速查表 |