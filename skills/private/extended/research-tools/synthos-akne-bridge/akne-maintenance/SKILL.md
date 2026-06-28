---


name: akne-maintenance
description: 维护个人知识库系统AKNE — 图谱诊断、修复、向量填充、源文件覆盖、Wiki清理、自动进化守护。覆盖AKNE仓库的完整运维生命周期。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: 维护个人知识管理系统AKNE — 图谱诊断、修复、向量填充、源文件覆盖、Wiki清理、自动进化守护。
    signature: 'akne_state: str -> maintenance_report: dict'
    related_skills: []


---


## IO_CONTRACT

- **input**: `component: str, action: str` — 用户请求描述、上下文信息
- **output**: `maintenance_result: dict — AKNE维护结果`

> 对应原则：P2（机械原子暴露输入输出规范）


io_contract:
  input:
    - 'akne_state: str -> maintenance_report: dict'
  output:
    - 'maintenance_report: dict (node_counts: int, edge_counts: int, health_score: float, issues: list[str])'
---




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

## 全面审计与修复流程（新增 2026-06-13）

> 当需要系统性修复AKNE知识库时，按此五阶段流程执行。
> 参考审计报告格式：/tmp/akne-audit-report.md（可作为模板）。

### 阶段1：结构健康诊断

```
1. 统计节点数、边数、按类型分布
2. 检查孤立节点（无边连接的节点）
3. 检查重名节点（同一 name 对应多个节点）
4. 检查边类型矛盾（同一节点对有多种 link_type）
5. 检查自环边（source == target）
```

### 阶段2：内容一致性检查

```
1. 读取关键源文件内容，提取核心主张
2. 对比不同文件间的矛盾声明（如：虹膜半径=眼球半径×2 vs 独立参数）
3. 查找单位错误（如：耳石密度 nm vs μm，差1000倍）
4. 查找方法迭代痕迹（单椭圆 vs 双椭圆，哪个是基线哪个是改进）
5. 标注矛盾文件的 version、controversial、superseded_by 字段
```

### 阶段3：研究空白识别

```
对每个研究领域检查：
- 数学推导是否完整？
- 实验验证是否充分？
- 与现有文献的对比是否建立？
- 临床转化路径是否清晰？
```

### 阶段4：科学假设提取

```
从研究中提炼可检验假设 H1, H2, H3...
格式：Hn: [条件] → [预测结果]，附验证难度(低/中/高)和优先级(P0/P1)
```

### 阶段5：执行修复

```
按优先级执行：
1. 紧急修正（阻塞研究正确性的错误）
2. 高优：版本簇合并（保留最大/最新文件，删除其余）
3. 高优：矛盾标注（在文件 metadata 中添加版本/矛盾信息）
4. 中优：草稿清理（小型草稿删除，大草稿保留参考）
5. 低优：孤立节点归档
```

### 关键陷阱（2026-06-13 新增）

#### 8. 文件删除 ≠ 图更新

删除源文件后，graph.json **不会自动更新**。必须：
- 先删除文件
- 再运行磁盘-图谱同步脚本
- 检查 graph.json 中是否还有已删除文件的节点/边
- 手动清理 graph.json 中的孤立引用

```python
# 同步检查：对比磁盘文件和图谱
# 磁盘文件在但图不在 → 需要添加
# 图在但磁盘不在 → 需要删除
```

#### 9. 批量删除边会误伤"保留文件"

当删除重复文件的边时，**保留文件**（keeper）的类别边可能一并被清除。修复：
- 删除边后，检查所有 source 节点的类别边是否完整
- 对孤立 source 节点，重新添加 `source_category_membership` 和 `source_category` 边
- 检查孤立 source_category 节点（如 `sources/工作站/archive`），如已无文件指向应删除

#### 10. 路径格式不一致

AKNE graph.json 使用 `.knowledge/sources/...` 相对路径，磁盘使用绝对路径 `/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/sources/...`。同步时需注意路径规范化：
- 磁盘路径 → 相对路径：去掉 `/media/yakeworld/sda2/academic_writer/yakeworld/` 前缀
- 图路径 → 磁盘路径：加上完整前缀

#### 11. 源文件路径双重化导致节点分裂（2026-06-18）

AKNE 源文件节点存在 `.knowledge/sources/xxx` 和 `sources/xxx` 两种格式同时存在的情况。同一源文件在图中有两个节点、两个集合边，导致：
- 连通率骤降（从 100% 到 ~56%）
- 边引用不存在的 `.knowledge/` 路径节点
- 向量记录重复（同一文件两条 embedding）

**诊断**：检查 `graph.json` 中是否有 `.knowledge/sources/` 前缀的节点。如果有，即存在分裂。

**修复**（按顺序执行）：
```python
# 1. 重命名：将 .knowledge/sources/xxx 节点 → sources/xxx
# 2. 修复所有指向 .knowledge/ 的边 → 指向 sources/ 版本
# 3. 删除原始 .knowledge/ 节点
# 4. 检查连通率，应为 99.9%+
```

脚本：`/tmp/akne-unify-names-v6.py` 或 `akne-vectorize.py`（含路径统一逻辑）。

**根因**：桥接脚本在历史版本中产生过 `.knowledge/` 前缀路径，新桥接产生 `sources/` 无前缀路径。两代节点共存。

**预防**：统一使用 `sources/xxx`（无 `.knowledge/` 前缀）作为 AKNE 节点名称标准格式。写入 `metadata.source_file` 时使用此格式。

#### 11b. /home/yakeworld/Synthos 是符号链接（2026-06-18）

`/home/yakeworld/Synthos/` 是 `/media/yakeworld/sda2/Synthos/` 的符号链接（inode 178178）。使用任何一个路径操作文件系统效果相同。

**影响**：技能审计时不应将两个路径视为独立目录。`~/.hermes/skills/` 是独立目录（20个hermes独有技能），不与Synthos重复。

**验证**：`stat -c '%i' /home/yakeworld/Synthos/ /media/yakeworld/sda2/Synthos/` 应返回相同inode。

**建议**：删除 `/home/yakeworld/Synthos` 符号链接以消除文件系统冗余。脚本和配置统一使用 `/media/yakeworld/sda2/Synthos/`。

#### 12. 论文目录路径错位（2026-06-18）

论文实际路径：`/media/yakeworld/sda2/Synthos/outputs/papers/<name>/state.json`
而非记忆中记录的：`/home/yakeworld/Synthos/papers/<name>/state.json`

**诊断**：`os.path.exists(paper_dir)` 为 False 不代表论文不存在，可能是路径错误。

**修复**：用 `find` 搜索 `state.json` 文件，确认论文实际存放位置。

#### 13. state.json  schema 不一致（2026-06-18）

论文 state.json 有 30+ 种不同 schema。有些有 `title`/`abstract`，有些只有 `quality_score`/`gate_status`，有些只有 `steps_completed`/`last_updated`。

**修复**：迭代 state.json 所有 key-value，提取任何标量/字典/列表值，不假设固定 schema。对于无 title/abstract 的论文，提取所有可用字段生成嵌入内容。

#### 14. 向量嵌入路径映射（2026-06-18）

向量数据库 `vectors.db` 中的旧嵌入使用 `.knowledge/sources/xxx` 路径，新节点使用 `sources/xxx` 路径。必须删除旧嵌入后重新生成。

**修复流程**：
```sql
DELETE FROM vectors;  -- 清除旧嵌入
-- 重新运行 akne-vectorize.py
```

#### 15. 论文磁盘映射缺失（2026-06-18）

graph.json 中有 171 篇论文节点，但磁盘上只有 134 篇实际存在。24 篇已不在磁盘上（已删除/归档/移动），37 篇不在 `/media/yakeworld/sda2/Synthos/outputs/papers/` 目录中。

**策略**：只向量化磁盘上存在的论文。对于不存在的论文，在图谱中保留节点但跳过向量嵌入。

#### 16. fuzzy_node_search 返回嵌套 tuple 导致搜索崩溃（2026-06-18）

`akne-enhanced-search.py` 中 `fuzzy_node_search` 在 `best=None` 时返回 `(None, 0.0)` 作为 `confidence`，实际返回的是 `(None, (None, 0.0))` —— 一个嵌套 tuple。调用方做 `confidence:.3f` 格式化时崩溃：`TypeError: unsupported format string passed to tuple.__format__`。

**根因**：`return best, min(0.8, best_score / 5.0) if best else (None, 0.0)` — Python 的 ternary `if/else` 优先级低于逗号，实际解析为 `return best, (min(0.8, best_score / 5.0) if best else (None, 0.0))`。当 `best=None`，返回 `(None, (None, 0.0))`。

**修复**：`return (best, min(0.8, best_score / 5.0)) if best else (None, 0.0)` — 用括号包裹三元表达式的返回值为 tuple。

**预防**：任何 `return a, b if cond else c` 的模式，必须显式加括号 `return (a, b if cond else c)`，因为 Python 逗号优先级高于三元表达式。

### 文件去重策略

两级匹配：
1. **精确 basename 匹配**：同一文件名在不同目录 → 真正重复，保留最大文件
2. **激进 stem 匹配**：去除日期/版本后缀后比较 → 发现版本簇，保留最新/最大版本

### 矛盾标注规范

在源文件 metadata 中记录：
```json
{
  "version": "2.0",
  "notes": "【矛盾标注】此处假设X。其他文件假设Y。",
  "controversial": "true",
  "superseded_by": "文件名.md",
  "supersedes": ["旧文件名.md"]
}
```

### 质量目标（2026-06-13 修复后）

| 指标 | 当前值 |
|------|--------|
| 图谱连通性 | 100% (1440/1440) |
| 源文件覆盖率 | 100% (1118/1118) |
| Wiki占位符污染 | 0行 |
| 边格式统一 | 100% link_type |
| 向量记录 | 533 (45%覆盖率) |
| Synthos论文孤立 | 0 (148/148) |
| Synthos技能孤立 | 0 (25/25) |
| 孤立节点 | 0 |
| 总边数 | 5893 |
| 总节点数 | 1440 |

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
| `references/audit-report-template.md` | 全面审计报告模板 — 五阶段结构（健康诊断→内容矛盾→研究空白→假设→修复） |
| `references/path-redundancy-2026-06-18.md` | 路径冗余诊断 — /home/yakeworld/Synthos 是 /media/.../Synthos 的符号链接，inode相同 |
| `scripts/akne-comprehensive-audit.py` | 16项综合健康审计脚本 — 一次运行覆盖连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式/元数据/Wiki污染/entity命名空间/路径前缀等全部指标 |

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
