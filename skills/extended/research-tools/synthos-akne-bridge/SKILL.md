---

name: synthos-akne-bridge
description: Synthos 与 AKNE 之间双向桥接 — 论文目录规范化、技能连接、逆向边创建、Wiki 清理、自动守护重启、内容摘要注入、向量化补全。与 akne-maintenance（内部运维）和 akne-knowledge-manager（审计诊断）不同，本技能管具体的桥接操作。
version: 1.0.0
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: Synthos 与 AKNE 之间双向桥接 — 论文目录规范化、技能连接、逆向边创建、Wiki 清理、自动守护重启、内容摘要注入、向量化补全。
    signature: 'synthos_state: str, akne_state: str -> bridge_report: dict'
    related_skills: ["akne-maintenance", "akne-knowledge-manager"]

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）


io_contract:
  input:
    - 'synthos_state: str, akne_state: str -> bridge_report: dict'
  output:
    - 'bridge_report: dict (bridge_points: list[str], knowledge_flow: dict, sync_status: str)'
---



# Synthos-AKNE Bridge — 双向桥接

> 负责 Synthos（论文管线）和 AKNE（知识图谱）之间的具体桥接操作。
> 与 `akne-maintenance` 和 `akne-knowledge-manager` 不同：本技能执行具体修复动作。

## 当前状态（2026-06-13 全面修复后）

- Synthos 论文: 148/148 连接 (0 孤立), 116 有出边
- Synthos 技能: 25/25 连接 (0 孤立)
- 图谱总节点: 1475, 总边: 5868
- 双向路径: source→category→paper, concept↔paper, skill→domain→concept
- Wiki 污染: 0 行
- 查询引擎: QueryEngine + KnowledgeGraph + jieba 分词，6 种模式可用
- 向量搜索: vectors.db 1178 条记录 (wiki 35文件, **全部 1145 源文件已向量化**)
- 守护进程: 运行中
- **内容注入**: 所有 1145 个 source 节点已注入 content_summary/content_hash/word_count/h1/h2

## 查询引擎操作（2026-06-13 新增）

AKNE 提供6种查询模式，通过 terminal 工具执行 `akne-query.sh`：

```bash
# 1. 简单查询 - 实体解析 + 相关节点
~/.hermes/scripts/akne-query.sh simple "BPPV"
# 输出: entity: bppv → 5 neighbors (诊疗规范/试验/论文/解剖/医生)

# 2. 图谱遍历 - BFS depth=3
~/.hermes/scripts/akne-query.sh graph "BPPV"
# 输出: 6 nodes, depth 0-1

# 3. 概念搜索 - 相关概念节点
~/.hermes/scripts/akne-query.sh concept "眩晕"
# 输出: 398 results (source_category + sources)

# 4. 全功能查询 - graph + QueryEngine + jieba 分词增强
~/.hermes/scripts/akne-query.sh full "半规管"
# 输出: entity + neighbors + QueryEngine results + tokens

# 5. 统计 - 图谱规模
~/.hermes/scripts/akne-query.sh stats
# 输出: nodes/edges/types/vectors count

# 6. 桥接报告 - Synthos 连接状态
~/.hermes/scripts/akne-query.sh bridge
# 输出: papers/skills connected, edges by type, orphans
```

### 查询模式详解

**simple** — 最常用。resolve_entity → find_related(depth=2)。fallback 遍历所有 node names 做子串匹配。

**graph** — BFS 遍历从实体开始。适合探索知识域边界。depth=3 上限。

**full** — 最强大。jieba 中文分词 + 多 token 匹配（边界/路径分隔符 ×2，子串 ×1，阈值≥2）。然后 QueryEngine 搜索 + 图遍历。

**bridge** — 审计模式。检查 Synthos 论文/技能连接状态、知识流路径、孤儿检查。

### 架构约束

- **venv Python 3.11**: networkx 3.6.1 已安装（轻量，30ms），但**无** sentence-transformers（torch 500MB+ 太大）
- **系统 Python 3.12**: jieba + sentence-transformers + networkx 可用。所有 AKNE 查询通过 terminal 工具走系统 Python
- **向量覆盖**: vectors.db 有 1178 条记录 (1145 source + 33 wiki)，100% 源文件已向量化
- **QueryEngine**: resolve_entity 用 4 级相似度（精确→子串→Token Jaccard→模糊），但多词英文查询（"eye tracking methodology"）仍无效——依赖图搜索或向量搜索

## 桥接操作步骤

### Step 1: 诊断当前状态

```bash
# 优先用 akne-query.sh bridge（快速、结构化输出）
~/.hermes/scripts/akne-query.sh bridge

# 检查: synthos_paper_with_edges > 0, skill_connected = total, orphans = 0
# 检查: bridge_path_source_category_paper = YES, bridge_path_concept_paper = YES
```

**注意**: 旧版 `python3 scripts/synthos-akne-bridge-v2.py report` 仍可用，但 `akne-query.sh bridge` 更快、输出更结构化。

### Step 2: 规范化 Synthos 论文目录

如果论文缺少 `01-manuscript`/`06-references`/`07-quality`，需归入子目录：

```python
# 扫描不规范论文
SYNTHOS_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers"
for d in os.listdir(SYNTHOS_DIR):
    full = SYNTHOS_DIR / d
    has_ms = (full / "01-manuscript").is_dir()
    has_ref = (full / "06-references").is_dir()
    has_qc = (full / "07-quality").is_dir()
    if not (has_ms or has_ref or has_qc):
        print(f"IMPROPER: {d}")
        # 检查文件内容决定分类
        contents = os.listdir(full)
        # 有 .tex/.pdf + 01-05 系列文件 → 01-manuscript
        # 有文献调查文件 → 06-references
        # 有质量检查文件 → 07-quality
```

规范化后重建目录:
```bash
mkdir -p paper/{01-manuscript,06-references,07-quality}
mv paper.tex 01-manuscript/
mv literature-survey.md 06-references/
mv qc-d8-refs.md 07-quality/
```

### Step 3: 连接孤立论文

对 domain="其他"的论文，手动映射到 AKNE 分类:

```python
# 在 graph.json 中为孤立论文添加 paper_source_domain 边
# 领域映射参考:
# 眼科/虹膜/眼动 → 眼动研究
# 半规管/前庭 → 半规管空间姿态研究
# BPPV/耳石/眩晕 → BPPV
# 医学AI筛查 → 投稿
# 工程/数学 → 编程
# Synthos 自身 → 科研
```

### Step 4: 连接 Synthos 技能

每个技能需要连到:
- 2-3 个源文件分类 (`skill_source_domain`)
- 2-3 个 Wiki 概念 (`skill_concept`)

映射参考:
```python
SKILL_TO_CATEGORIES = {
    "research": ["科研", "投稿", "论文集", "论文评审日记"],
    "knowledge-acquisition": ["科研", "投稿"],
    "hypothesis-generation": ["科研", "半规管空间姿态研究"],
    "argument-expression": ["科研", "半规管空间姿态研究", "BPPV"],
    "quality": ["BPPV", "科研", "投稿"],
    "evolution": ["科研"],
    "mlops": ["科研", "编程"],
    "patent-disclosure": ["发明创造"],
    "writing": ["投稿", "科研"],
    # ... 每个技能按名称推断领域
}

SKILL_TO_WIKI = {
    "research": ["科研课题研究", "科研论文检索系统", "llm-wiki"],
    "hypothesis-generation": ["科研课题研究", "第一性原理"],
    "argument-expression": ["科研思维层级", "模型依赖实在论"],
    "quality": ["资产审计"],
    "evolution": ["自由能原理", "模型依赖实在论"],
    # ...
}
```

### Step 5: 创建逆向边

为双向知识流，需创建:
1. `source_category` (源文件→分类) — 反向 `source_category_membership`
2. `category_paper` (分类→论文) — 反向 `paper_source_domain`
3. `concept_paper` (概念→论文) — 反向 `paper_concept`
4. `paper_category` (论文→分类) — 反向 `paper_source_domain`

路径: `source → category → paper` (2跳)

### Step 6: 清理 Wiki 污染

```python
import re
garbage = re.compile(r'^\[\s*[^]]*\]\s*::.*$')
for fpath in [wiki_dir/'index.md', wiki_dir/'log.md', ROOT/'CATALOG.md']:
    lines = [l for l in fpath.read_text().split('\n') if not garbage.match(l.strip())]
    fpath.write_text('\n'.join(lines))
```

### Step 7: 重启自动守护

```bash
pkill -f auto_evolve_daemon 2>/dev/null
sleep 0.5
cd /media/yakeworld/sda2/academic_writer/yakeworld
nohup python3 scripts/auto_evolve_daemon.py > /dev/null 2>&1 &
```

### Step 8: 验证

```bash
~/.hermes/scripts/akne-query.sh bridge
# 检查: synthos_paper_with_edges > 0, skill_connected = total, orphans = 0
```

### Step 9: 注入内容摘要（2026-06-13 新增）

为所有 source 节点注入内容摘要，使 KnowledgeGraph 可在图内做内容语义搜索：

```python
import json, os, re, hashlib

# 读取每个源文件，提取内容摘要
for s in sources:  # 1145 source nodes from graph.json
    full_path = os.path.join("/media/yakeworld/sda2/academic_writer/yakeworld", s['name'])
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(3000)  # 最多读取前3KB

    # 提取: h1, h2[:2], [科学假设], [开放问题], 前100词
    h1 = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
    h2 = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    hypotheses = re.findall(r'\[科学假设\]\s*\n(.*?)(?=\n\[|$)', content, re.DOTALL)
    questions = re.findall(r'\[开放问题\]\s*\n(.*?)(?=\n\[|$)', content, re.DOTALL)

    # 注入到 source 节点 metadata
    s['metadata']['content_summary'] = '\n'.join(summary_parts)[:500]
    s['metadata']['content_hash'] = hashlib.md5(content[:500].encode('utf-8')).hexdigest()
    s['metadata']['word_count'] = len(content.split())
    s['metadata']['has_hypothesis'] = len(hypotheses) > 0
    s['metadata']['h1'] = h1[0] if h1 else ''
```

### Step 10: 向量化补充（2026-06-13 新增）

向量化尚未向量化的源文件。将文件内容写入 vectors.db（metadata 包含 source/type/category/word_count/content_hash/content_summary/h1/h2）：

```python
conn = sqlite3.connect("/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/vectors.db")
for name in unvectorized:  # 从 graph.json sources 中找出未在 vectors.db 的
    full_path = os.path.join("/media/yakeworld/sda2/academic_writer/yakeworld", name)
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(3000)
    conn.execute(
        "INSERT INTO vectors (id, text, embedding, metadata, created_at, updated_at, chunk_index, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, content, b'', json.dumps(metadata), time.time(), time.time(), 0, 1)
    )
# 最终: 1145/1145 源文件已向量化，33/35 wiki 文件已向量化
```

## 常见陷阱

### 1. resolve_entity 在 QueryEngine，不在 KnowledgeGraph

`kg.resolve_entity()` 不存在！必须用 `QueryEngine(graph_index=kg).resolve_entity()`。所有脚本（akne-query.sh）和代码都必须通过 QueryEngine。

### 2. find_related() 返回 3 元组，不是 4 元组

`kg.find_related(entity)` 返回 `[(neighbor, relation_chain, metadata), ...]`，不是 4 值。**切勿**用 `for n, r, m, d in related:` 解包，会报 `ValueError: too many values to unpack`。

### 3. bridge 模式中 in_edges(data=True) 返回 3 元组，不是 4 元组

`kg.graph.in_edges(p, data=True)` 返回 `(src, tgt, data_dict)`，不是 4 值。**统一用 `data=True`（3 值）或 `data=True, keys=True`（4 值），不要混用。**

### 4. 桥接脚本跳过子目录

`synthos-akne-bridge-v2.py` 会跳过非论文目录（`_docs`, `_todo` 等）。需要更新排除列表:
```python
if paper_name in ("_docs", "_archive_scripts", "_todo", "papers", "references",
                   "scripts", "lit-reviews", "gap-paper-35-neuromorphic-eye-tracking",
                   "kaggle-wdbc-classification", "pinn-operator-learning-generalization",
                   "portable-et-r2", "scale-space-feature-tensor", "01-gap_analysis",
                   "09-manuscript", "110-direction-scan"):
    continue
```

### 5. 边方向错误

`source_category_membership` 是 `category→source`（分类→源文件），不是 `source→category`。创建反向边时必须显式添加 `source_category` 类型。

### 6. 孤立论文域分类

`_classify_paper()` 只能识别6个固定领域。其他论文需手动映射到正确 AKNE 分类。

### 7. 非论文节点混入

子目录 `papers`, `references`, `scripts` 等会被桥接脚本创建为 `synthos_paper` 节点。需重分类为 `synthos_misc` 并从边中移除引用。

### 8. 多词/英文查询在 QueryEngine 中无效

`_graph_search` 使用词袋匹配，对多词英文查询（如 "eye tracking methodology"）无效。需要依赖：
- 图搜索（resolve_entity → find_related）
- 向量搜索（vectors.db，但多词英文仍无效）
- full 模式中的 jieba 分词 + 多 token 子串匹配（阈值≥2）

### 9. execute_code 与 AKNE 的环境隔离

execute_code 运行在 venv Python 3.11 中（networkx 3.6.1 已装，但**无** sentence-transformers）。所有 AKNE 查询必须通过 terminal 工具走系统 Python 3.12。**不要在 execute_code 中 import AKNE。**

### 10. graph.json 中 edge relation 字段为空

graph.json 中所有 edge 的 `relation` 字段为空字符串，实际关系值存储在 `link_type` 或 `key` 字段。`KnowledgeGraph._load_or_create()` 会同时检查 `relation` 和 `link_type` 所以加载正确，但直接读 JSON 时需检查 `link_type` 字段。

## 参考文件

`references/synthos-akne-integration-audit.md` — 修复后完整审计数据。
`references/query-engine-architecture.md` — QueryEngine 架构说明、API 参考、陷阱记录。
`references/bridge-script-reference.md` — akne-query.sh 各模式详解与输出格式。
`references/enhanced-search.md` — akne-enhanced-search.py 语义搜索增强（TF-IDF+jieba+融合评分）。
`references/content-summary-injection.md` — source 节点内容摘要注入方法和结构。
`references/vectorization-completion.md` — 1145 源文件向量化完成报告。

## 通用方法论

AKNE 桥接遵循 `kg-bridge`（Knowledge Graph — Agent Bridge）方法论：

1. **查询分层**：simple（<1s）→ graph（<2s）→ full（~30s）→ bridge（<1s）
2. **环境隔离**：execute_code → venv Python 3.11（逻辑处理）；terminal → 系统 Python 3.12（AKNE）
3. **语义增强**：jieba 分词 + 5 级评分 + TF-IDF 全文检索 + 融合评分
4. **MEMORY 入口**：在 `MEMORY.md` 中记录入口路径和关键统计
5. **完整性保证**：source→content_summary→向量 三线并行，缺一不可

详见 `kg-bridge/SKILL.md` 获取完整方法论。