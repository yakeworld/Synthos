# Synthos Obsidian 知识库搭建记录 (2026-05-27)

> 将 `~/Synthos` 项目目录初始化为可导航的 Obsidian 知识库

## 最终结构

```
Synthos/                          ← 在 Obsidian 中直接打开
├── _INDEX.md                     ← 根 MOC
├── .obsidian/                    ← 图谱、反链、标签
├── .gitignore                    ← 含 .obsidian/
│
├── docs/_INDEX.md                ← 架构/哲学文档索引
├── skills/_INDEX.md              ← 7 认知原子索引
├── papers/_INDEX.md              ← 论文笔记索引
├── experiments/_INDEX.md         ← 实验记录索引
├── evolution/_INDEX.md           ← 进化里程碑索引
├── competition/_INDEX.md         ← 竞赛材料索引
│
├── outputs/papers/_INDEX.md      ← 论文原文源文件索引（含转换状态）
├── outputs/papers/*/paper.md     ← 8 篇论文 Markdown 版
├── outputs/papers/*/ → symlink  ← TeX/PDF/图表
│
└── scripts/
    └── obsidian_to_factstore.py  ← Obsidian → fact_store 同步脚本
```

## 关键教训

1. **两层分离**: `papers/`（笔记层） vs `outputs/papers/`（源文件层），避免混淆分析 vs 原文。
2. **MOC 链**: 每个子目录的 `_INDEX.md` 构成面包屑导航，根 MOC 汇总所有区域。
3. **frontmatter 策略**: 只给关键文档加 frontmatter（哲学文档、技术路线图），不必要全部覆盖。
4. **符号链接优于复制**: 保持源文件在原始位置，vault 只建引用。Git 不跟踪 vault 元文件。
5. **同步脚本**: `obsidian_to_factstore.py` 扫描 vault 变更 → 提取关键事实 → 写入 `fact_store`。

## 文件清单

### 新建 MOC 文件 (8个)
- `_INDEX.md` — 根 MOC
- `docs/_INDEX.md` — 架构文档
- `skills/_INDEX.md` — 认知原子
- `papers/_INDEX.md` — 论文笔记（含 outputs/papers 链接）
- `outputs/papers/_INDEX.md` — 论文原文（含转换状态表）
- `experiments/_INDEX.md` — 实验记录
- `evolution/_INDEX.md` — 进化引擎
- `competition/_INDEX.md` — 竞赛材料

### 添加 frontmatter 的文件 (3个)
- `docs/synthos-philosophy.md`
- `docs/技术路线图.md`
- `docs/智能体建设说明书.md`

### 论文笔记 (2个)
- `papers/3WD三分诊断方法论.md`
- `experiments/三文证漏实验.md`
