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
3. **反向边** — source_category (1145), category_paper (255), paper_category (255), concept_paper (281)
4. **孤立论文映射** — 37篇"其他"域论文手动映射到 BPPV/眼动研究/投稿 等分类
5. **非论文节点清理** — 7个目录重新分类为 synthos_misc
6. **桥接脚本更新** — 排除列表增加 15 个非论文目录名
7. **Wiki 清理** — 去除 index.md 和 log.md 中所有 `[X]::` 垃圾行
8. **守护重启** — auto_evolve_daemon.py 每900秒重新运行

## 当前图谱统计

### 节点 (1475)
| 类型 | 数量 |
|------|------|
| source | 1145 |
| synthos_paper | 148 |
| synthos_skill | 25 |
| entity | 126 |
| source_category | 24 |
| synthos_misc | 7 |

### 边 (6130)
| 边类型 | 数量 | 方向 |
|--------|------|------|
| source_co_occurrence | 1970 | 双向 |
| source_category_membership | 1145 | category→source |
| source_category | 1145 | source→category |
| paper_concept | 335 | paper→concept |
| concept_paper | 281 | concept→paper |
| paper_source_domain | 285 | paper→category |
| category_paper | 255 | category→paper |
| paper_category | 255 | paper→category |
| domain_overlap | 252 | 双向 |
| references | 137 | 通用 |
| skill_source_domain | 42 | skill→category |
| skill_concept | 18 | skill→concept |
| paper_source_match | 10 | 名称匹配 |

### 连通性
- 连通节点: 1468/1475 (99.5%)
- 孤立节点: 7 (全部为 synthos_misc 子目录)
- 孤立论文: 0/148
- 孤立技能: 0/25

## 双向路径示例
- `source file → category → synthos paper` (2跳)
- `wiki concept → synthos paper → wiki concept` (3跳闭环)
- `synthos skill → category → synthos paper` (2跳)
- `source file → category ← synthos paper` (互连)

## 排除的非论文目录 (bridge-v2.py 已更新)
`_docs`, `_archive_scripts`, `_todo`, `papers`, `references`, `scripts`, `lit-reviews`,
`gap-paper-35-neuromorphic-eye-tracking`, `kaggle-wdbc-classification`, `pinn-operator-learning-generalization`,
`portable-et-r2`, `scale-space-feature-tensor`, `01-gap_analysis`, `09-manuscript`, `110-direction-scan`
