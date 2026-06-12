------
name: synthos-akne-bridge
description: Synthos 与 AKNE 之间双向桥接 — 论文目录规范化、技能连接、逆向边创建、Wiki 清理、自动守护重启。与 akne-maintenance（内部运维）和 akne-knowledge-manager（审计诊断）不同，本技能管具体的桥接操作。
triggers:
  - 
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: Synthos 与 AKNE 之间双向桥接 — 论文目录规范化、技能连接、逆向边创建、Wiki 清理、自动守护重启。
    signature: 'synthos_state: str, akne_state: str -> bridge_report: dict'
    related_skills: [akne-knowledge-manager, akne-maintenance, knowledge-extraction, knowledge-acquisition, paper-pipeline]
---
  io_contract: input: ['synthos_state: str, akne_state: str -> bridge_report: dict', 'output: ['bridge_report: dict (bridge_points: list[str], knowledge_flow: dict, sync_status: str)']




# Synthos-AKNE Bridge — 双向桥接

> 负责 Synthos（论文管线）和 AKNE（知识图谱）之间的具体桥接操作。
> 与 `akne-maintenance` 和 `akne-knowledge-manager` 不同：本技能执行具体修复动作。

## 当前状态（2026-06-10 修复后）

- Synthos 论文: 148/148 连接 (0 孤立)
- Synthos 技能: 25/25 连接 (0 孤立)
- 图谱总节点: 1475, 总边: 6130
- 双向路径: source→category→paper, concept↔paper, skill→domain→concept
- Wiki 污染: 0 行
- 守护进程: 运行中
- **注意**: 2026-06-10 修复了 `akne/graph/graph_index.py` 的 4 个 bug（out_edges 解包、link_type/relation 字段映射、traverse 键查找、BFS 循环），QueryEngine 现在可用。但仍有限制：resolve_entity 阈值 0.5、未配置向量搜索。

## 桥接操作步骤

### Step 1: 诊断当前状态

```bash
cd /media/yakeworld/sda2/academic_writer/yakeworld
python3 scripts/synthos-akne-bridge-v2.py report
```

检查:
- `synthos_isolated`: 应为 0
- `isolated`: 应 ≤10（仅杂项）
- 检查 `paper_concept`, `concept_paper`, `source_category`, `category_paper` 是否都 >0

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
python3 scripts/synthos-akne-bridge-v2.py report
# 检查: synthos_isolated=0, 所有 skill 已连接, 所有关键边类型>0
```

## 常见陷阱

### 1. 桥接脚本跳过子目录

`synthos-akne-bridge-v2.py` 会跳过非论文目录（`_docs`, `_todo` 等）。需要更新排除列表:
```python
if paper_name in ("_docs", "_archive_scripts", "_todo", "papers", "references", 
                   "scripts", "lit-reviews", "gap-paper-35-neuromorphic-eye-tracking",
                   "kaggle-wdbc-classification", "pinn-operator-learning-generalization",
                   "portable-et-r2", "scale-space-feature-tensor", "01-gap_analysis",
                   "09-manuscript", "110-direction-scan"):
    continue
```

### 2. 边方向错误

`source_category_membership` 是 `category→source`（分类→源文件），不是 `source→category`。创建反向边时必须显式添加 `source_category` 类型。

### 3. 孤立论文域分类

`_classify_paper()` 只能识别6个固定领域。其他论文需手动映射到正确 AKNE 分类。

### 4. 非论文节点混入

子目录 `papers`, `references`, `scripts` 等会被桥接脚本创建为 `synthos_paper` 节点。需重分类为 `synthos_misc` 并从边中移除引用。

## 参考文件

`references/synthos-akne-integration-audit.md` — 修复后完整审计数据。