---
name: akne-knowledge-manager
description: AKNE 知识管理系统的双向整合审计、Synthos-桥接诊断、知识流分析、内容级审计。与 akne-maintenance 不同，专注两系统间的连接质量及知识内容质量而非内部运维。
version: 1.0.0
triggers:
  - 需要审计 AKNE 知识库内容质量（矛盾检测、版本簇、研究空白）
  - 需要 Synthos 与 AKNE 双向整合检查
  - 需要跨系统连接诊断和知识流分析
metadata:
  synthos:
    priority: P1
    atom_type: domain-skill
    description: "AKNE 知识管理系统的双向整合审计、Synthos-桥接诊断、知识流分析、内容级审计"
    signature: 'akne_graph: str, synthos_graph: str -> integration_report: dict + content_audit: dict'
    related_skills: ["akne-knowledge-manager", "akne-maintenance"]
io_contract:
  input:
    - 'akne_graph: str, synthos_graph: str -> integration_report: dict + content_audit: dict'
  output:
    - 'integration_report: dict (bridge_points: list[str], knowledge_flow: dict, issues: list[str])'
    - 'content_audit: dict (contradictions: list, version_clusters: list, research_gaps: list, hypotheses: list)'

---

## IO_CONTRACT

- **input**: `knowledge_type: str, action: str` — 用户请求描述、上下文信息
- **output**: `result: dict — AKNE知识管理`

> 对应原则：P2（机械原子暴露输入输出规范）




# AKNE Knowledge Manager — 整合审计 + 内容级审计

> 专注 Synthos 与 AKNE 之间的双向整合质量 + 知识内容质量。
> 与 `akne-maintenance` 的区别：后者管内部运维（诊断、修复、向量填充），本技能管跨系统连接和内容质量。

## 核心问题

Synthos 是论文产出管线，AKNE 是个人知识图谱。两者通过 `synthos-akne-bridge-v2.py` 桥接。
内容质量问题：版本冗余、矛盾声明、研究空白、假设不明确。

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

## 当前状态（2026-06-13 审计后）

### 图谱统计

| 指标 | 值 | 备注 |
|------|-----|------|
| 总节点 | 1475 | |
| 总边 | 6130 | |
| 连通节点 | 1468/1475 (99.5%) | 7 孤立 synthos_misc |
| Synthos 论文 | 148（0孤立） | |
| Synthos 技能 | 25（0孤立） | |
| Synthos 杂项 | 7（子目录/非论文） | 孤立，可清理 |
| 版本簇 | 70+ | 跨多个研究领域 |
| 内容矛盾 | 3处 | 1处致命(单位错误) |
| 研究空白 | 5个 | Gap1-5 |
| 科学假设 | 7个 | H1-H7 |

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

## 内容级审计（2026-06-13 新增）

`akne-maintenance` 管运维，本技能管跨系统连接，**内容级审计**管知识质量。三者互补。

### 1. 内容矛盾检测

读取同主题源文件，提取"创新点"、"关键"、"假设"、"应该"、"不同于"、"错误"等信号词行，对比同一概念在不同文件中的声明。

典型矛盾类型：
- **数值矛盾**：同一参数在不同文件取值不同（如虹膜/眼球半径 2:1 vs 独立参数）
- **方法矛盾**：不同文件主张不同技术方案（单椭圆 vs 双椭圆），无版本标注
- **单位错误**：数量级错误（如耳石密度 nm vs μm，差1000倍）— 此为**致命级**矛盾
- **方法缺陷自述**：文件自己指出某种方法"存在缺陷"但未提供替代方案验证

检测方法：
```python
# 1. 读取同主题所有源文件（从 metadata.category 分组）
# 2. 提取关键声明行（含信号词：创新点/关键/假设/应该/不同于/错误/尚未/未知/问题/局限）
# 3. 对比同一概念在不同文件中的声明
# 4. 标注矛盾等级：致命(单位错误) / 严重(方法冲突) / 轻微(理解深化)
```

2026-06-13 审计发现 3 处矛盾：
1. **耳石密度单位错误（致命）** — `BPPV拟真参数设置.md` 中"半径 0.5~15nm"应为"μm"
2. **虹膜/眼球半径比例不一致（严重）** — 部分文件用 2:1 固定比例，部分作为独立参数
3. **单椭圆 vs 双椭圆（轻微）** — 两种方法并存但无版本关系标注

### 2. 版本簇管理

源文件按 basename stem（去除日期、-1/-2/-3、---草稿后缀）聚类。同 stem 的文件视为版本簇。

管理规则：
- 每个簇保留**最新/最完整**版本（按创建时间和文件大小判断）
- 其余文件标记为 `archived` 或移入 `archive/` 子目录
- 保留文件在 metadata 中新增 `version`, `replaces`, `supersedes` 字段
- 矛盾的文件标注 `controversial` 标记

2026-06-13 审计识别 70+ 版本簇，主要分布在：
- 双椭圆拟合（6 个版本）
- 3D眼球模型虹膜分割（4 个版本）
- 半规管空间姿态测量（4 个版本）
- 后半规管短臂侧结石（3 个版本）
- Dix-Hallpike 试验分析（3 个版本）

### 3. 研究空白识别

通过对比源文件中的"创新点"、"已有成果"和"尚未"、"未知"、"问题"等词，识别 5 类空白（2026-06-13 审计发现）：

| 编号 | 空白类型 | 示例 |
|------|---------|------|
| Gap 1 | 有框架缺验证 | 瞳孔虚像校正有数学框架但缺实验验证 |
| Gap 2 | 数学完整缺实验 | 3D虹膜椭圆反推数学完整但缺真实数据验证 |
| Gap 3 | 仿真框架有错 | BPPV物理引擎可运行但耳石密度参数单位错误 |
| Gap 4 | 概念完整缺转化 | 3D眼震分析概念完整但缺临床标准化图谱 |
| Gap 5 | 初步探索缺系统 | 跨疾病眼动标志物有初步文献但缺统一体系 |

### 4. 科学假设提取

从源文件中提取可检验假设的 3 步法：
1. 定位有明确量化目标的声明（如"误差 < X"、"准确率 > Y%"）
2. 定位有明确因果关系的假设（如"A 与 B 成反比"）
3. 标注验证难度（低/中/高）和优先级（P0/P1）

2026-06-13 审计提取 7 个假设（H1-H7），覆盖领域：
- 三维虹膜：H1（双椭圆误差<1px）、H2（3D分割Dice>0.95）、H6（角膜曲率反比关系）
- BPPV：H3（短臂侧漏诊率>60%）
- 三维眼动：H4（3D轨迹分类>95%）
- 跨疾病：H5（前庭特征=神经退行性疾病早期标志物）
- 半规管姿态：H7（法向量法优于夹角平均法）

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

### 图谱-磁盘同步（新增 2026-06-13）
删除文件后必须同步 graph.json：
1. 删除源文件
2. 运行磁盘扫描，列出所有 .md 文件
3. 对比 graph.json 中 source 节点：磁盘有但图无 → 添加节点；图有但磁盘无 → 删除节点+边
4. 检查被删除节点是否曾是某"保留文件"的同名副本 → 恢复这些保留文件的类别边
5. 检查 source_category 节点是否仍有文件指向 → 无指向的孤立 category 节点删除
6. 最终验证：孤立节点=0，论文连接=100%，技能连接=100%

**关键原则**：文件删除和图更新是两个独立操作，必须都完成才算修复完成。

### 文件去重策略（新增 2026-06-13）

两级匹配去重：
1. **精确 basename 匹配**：同一文件名在不同目录 → 真正重复，保留最大文件
2. **激进 stem 匹配**：去除日期/版本后缀后比较 → 发现版本簇（如 `文件名-1.md`/`文件名.md`），保留最新/最大版本

去重后必须恢复"保留文件"的类别边，否则这些文件会成为孤立节点。

### 致命内容矛盾修正
2026-06-13 发现：`BPPV拟真参数设置.md` 中"耳石半径 0.5~15nm"为**数量级错误**，应为 0.5~15mm 或 500~15000μm。
**修复**：直接修改源文件中的数值，并添加注释说明正确量级来源。

### 版本簇合并
2026-06-13 识别 70+ 版本簇。
**修复模式**：
1. 按 basename stem 聚类（使用 difflib.SequenceMatcher 或直接去后缀）
2. 对每个簇：按创建时间戳和文件大小确定"最终版"
3. 最终版保留，其余移入 `archive/` 或标记为 `archived`
4. 在最终版 metadata 中新增 `version`、`replaces`、`supersedes` 字段

### 文件矛盾标注
对有矛盾但非错误的文件（如 2:1 比例 vs 独立参数）：
**修复模式**：
1. 标注 `controversial: true`
2. 在 metadata 中新增 `controversy_note` 字段说明矛盾双方立场
3. 标注哪方是"已验证"、哪方是"假设"

## 搜索功能

AKNE 搜索通过 `.hermes/scripts/akne-enhanced-search.py` 实现，三层策略：
1. **实体解析** — 精确/子串/分词/fuzzy 匹配节点名
2. **图遍历** — 从解析实体出发 2 跳搜索相关节点
3. **TF-IDF 文本搜索** — 对 1118 个源文件构建索引（40615 词汇），支持中英混合

向量嵌入（1480 条，384 维）已生成并存入 `vectors.db`，脚本支持 `--mode full` 同时启用全部三层。

### 已知问题

- **性能偏慢**：单次 full-mode 搜索约 22 秒（含 TF-IDF 索引全部 1118 个源文件）
  - 建议：增量更新索引或预构建缓存
- **Graph 邻居过泛**：多数节点连接在 `sources/科研` 或 `sources/编程` 大类下，缺乏精细分类
  - 建议：按领域进一步拆分 source_category 节点

### Bug 修复记录

- **2026-06-18**：`fuzzy_node_search` 在 `best=None` 时返回 `(None, 0.0)` 嵌套 tuple，
  导致 `confidence:.3f` 格式化崩溃。修复：`return best, min(0.8, best_score / 5.0)` →
  `return (best, min(0.8, best_score / 5.0))`。

## 参考文件

- `references/synthos-akne-integration-audit.md` — 2026-06-10 修复后完整数据。含边类型分布、双向路径示例、诊断命令、修复历史。旧审计数据已归档替换。
- `references/content-audit-aug2026.md` — 2026-06-13 内容级审计详细记录。含 3 处矛盾详情、70+ 版本簇清单、5 个研究空白、7 个科学假设。
- `references/search-performance.md` — 2026-06-18 搜索功能测试报告。含四项查询结果、性能基准、各类查询的准确率评估。
- `references/akne-vs-obsidian.md` — AKNE 与 Obsidian 架构对比：为何自建知识图谱而非用现成工具。面向人 vs 面向机器的定位差异。

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
| 致命内容矛盾 | 修正数值/单位，添加注释 |
| 版本簇冗余 | 聚类→保留最终版→其余归档 |
| 文件矛盾 | 标注 controversial + 说明双方立场 |