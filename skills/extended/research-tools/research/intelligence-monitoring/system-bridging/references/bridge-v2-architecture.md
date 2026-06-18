# Bridge v2 架构详解

> 创建日期: 2026-06-07
> 对应: synthos-akne-bridge-v2.py

## 架构变化

### v1 → v2 关键改进

1. **边格式自动统一**: 每次同步自动将 `relation` → `link_type`，裸 `weight` → `link_type: domain_overlap`
2. **Category 中间层**: 源文件不直接连论文，而是通过 `sources/分类名` 节点
3. **增量同步**: `_exists_node()` + `_exists_edge()` 检查，不重复创建
4. **版本追踪**: `logs/bridge-log.jsonl` 每次记录变更

## 边类型体系

### 论文 → 源文件分类 (paper_source_domain, weight=0.6)

```
bppv-epley-semont-dizziness-mechanism → sources/BPPV
bppv-epley-semont-dizziness-mechanism → sources/投稿
kappa-3d-eye-tracking → sources/眼动研究
saccade-adaptation-pinn → sources/编程
```

映射规则: `DOMAIN_TO_CATEGORIES` 字典，根据论文名称推断领域，映射到 1-2 个分类。

### 论文 → Wiki概念 (paper_concept, weight=0.7)

```
bppv-epley-semont-dizziness-mechanism → bppv
bppv-epley-semont-dizziness-mechanism → 前庭解剖
kappa-3d-eye-tracking → 虚拟仿真研究
```

映射规则: `DOMAIN_TO_WIKI` 字典，基于名称重叠。

### 源文件内部连接

- `category → source` (1:N, weight=1.0) — 每个源文件属于一个分类
- `source ↔ source` (N:8, weight=0.3) — 同类源文件互连，限制每个文件最多7个

## 节点类型

- `entity` — 疾病、人物、工具（AKNE原生）
- `source` — 源文件（AKNE原生）
- `source_category` — 分类hub（优化后新增）
- `synthos_paper` — Synthos论文（桥接注入）
- `synthos_skill` — Synthos技能（桥接注入）
- `wiki` — Wiki页面（AKNE原生）

## 同步流程

1. 遍历 Synthos 论文目录
2. 对每个论文:
   a. 分类推断（BPPV / 眼动追踪 / 前庭生理 / 深度学习 / ODE-PINN / 临床诊断）
   b. 检查节点是否存在（不存在则创建）
   c. 创建论文→分类边（1-2个）
   d. 创建论文→Wiki概念边（基于domain→wiki映射）
3. 遍历 Synthos 技能目录
4. 检查节点是否存在（不存在则创建）
5. 统一所有边格式
6. 保存到 graph.json
7. 记录变更到 bridge-log.jsonl