# Synthos-AKNE 整合审计报告 — 2026-06-10 修复后

## 修复历史

### 修复前状态
| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| Synthos 论文连接 | 118/155 (76%) | 148/148 (100%) |
| Synthos 技能连接 | 0/25 | 25/25 (100%) |
| AKNE→Synthos 逆向 | 0 条 | 281 条 concept→paper |
| Wiki 垃圾行 | 56+ 行 | 0 |
| 自动守护 | 已停（1个月前） | 已重启 |
| 总边数 | 3842 | 6130 |

### 修复操作
1. **目录规范化** — 32篇论文创建 01-manuscript/06-references/07-quality 子目录
2. **技能连接** — 25个技能通过 skill_source_domain (42边) + skill_concept (18边) 连接
3. **反向边** — source_category (1145), concept_paper (281), category_paper (255), paper_category (255)
4. **Wiki清理** — 删除 index.md/log.md/CATALOG.md 中的 `[X, Y]::` 占位符垃圾
5. **守护重启** — auto_evolve_daemon.py 每 3600 秒循环

## 审计数据（2026-06-13 更新）

### 最新图谱统计
| 指标 | 值 |
|------|-----|
| 总节点 | 1475 |
| 总边 | 5868 |
| source | 1145 |
| synthos_paper | 148 |
| entity | 126 |
| synthos_skill | 25 |
| source_category | 24 |
| synthos_misc | 7 |

### 边类型分布
| 类型 | 数量 |
|------|------|
| source_co_occurrence | 1970 |
| source_category | 1145 |
| source_category_membership | 1145 |
| paper_concept | 335 |
| concept_paper | 281 |
| category_paper | 255 |
| paper_category | 255 |
| domain_overlap | 245 |
| references | 137 |
| skill_source_domain | 42 |
| skill_concept | 18 |
| paper_source_domain | 30 |
| paper_source_match | 10 |

### 连通性
- Synthos 论文: 148/148 有连接（139篇无出边，仅作为概念目标）
- Synthos 技能: 25/25 有连接
- 知识流路径: source→category→paper (2跳)

### API 调用（见 api-reference.md）
- KnowledgeGraph: kg.graph.nodes(), kg.graph.edges(), kg._nodes_by_type, kg._edges_by_type
- QueryEngine: resolve_entity(), query(), get_related_entities()
- 环境陷阱: execute_code 用 venv python3.11，AKNE 在系统 python3.12，必须用 terminal

## 已知问题

### 语义搜索局限
- 词袋(Jaccard)匹配，多词查询如 "eye tracking methodology" 无结果
- 向量数据库存在但未配置（需 vector_store 参数）
- resolve_entity 成功率有限

### Synthos 论文 139 篇无出边
仅作为 paper_concept 的目标存在，没有向外连接的边。这些论文是：
eye-head-coordination-PINN, 092-dissociated-ocular-torsion-PINN, corneoscleral-shell-ODE,
okr-adaptation-pinn, rop-ai-screening, glaucoma-ai-screening, vor-sparse-modular,
perilymph-hydropressure-ODE, pinn-operator-learning-generalization, optic-nerve-head-deformation-ODE...

### 向量空洞
vectors.db 有记录但无实际 embedding，需要 sentence-transformers + GPU。