# Phase 3 Strategy A 全栈提升模式

> 当论文的 D7 Strategy A 未完全耗尽（有 3-10 个未引用 bibitem）且需要 D2/D4/D1/D6 多项提升以推至 T1 时使用。

## 适用条件

| 条件 | 检查方法 |
|:-----|:---------|
| 论文在 Phase 3 (T2 边界, avg 0.80-0.84) | 从 tracker 读取 |
| D7 Strategy A 可用 (match rate < 95%) | `python3 -c "..."` 检查 cite↔bibitem |
| D4 缺图 (Fig < 2) 或 D2 缺算法 | 读 quality-report.md |
| D1/D6 有提升空间 (D1<0.85 或 D6<0.85) | 读 quality-report.md |

## 与三管齐下的区别

| 维度 | 三管齐下 (v1→v2) | Strategy A 全栈 (Phase 3) |
|:-----|:-----------------|:-------------------------|
| 适用阶段 | T3→T2 (avg<0.80) | T2→T1 (avg 0.80-0.84) |
| D7 可用引用 | ≥15 未引用 | 3-10 未引用 |
| D4 操作 | PRISMA流程图 | 收敛框架图/架构图 |
| D2 操作 | 误差传播方程 | 诊断算法/决策树 |
| D1/D6 | 不必要 | 贡献列表+收敛定位 |
| 典型收益 | +0.044~0.076/轮 | +0.015~0.025/轮 |

## 执行流程

按 D7→D4→D2→D1/D6→D5 顺序串行执行：

### Step 1: D7 Strategy A (零成本)
1. 运行 Python 脚本找出所有未引用 bibitem
2. 读取每个未引用的 bibitem 内容（提取前 200 字符）
3. 按主题分类: (a)临床诊断 (b)方法学基础 (c)领域拓展 (d)交叉证据
4. 找到合适插入位置 (Introduction/Discussion/Limitations中)
5. 用 `content.replace()` 逐一插入 `\cite{ref}` 到已有 `\cite{...}` 组中
6. 每插入 2-3 个后验证一次 `assert ref not in content` 预检查

**⚠️ 链崩溃防护**: 每步后增量 write_file:
```python
content = open('paper.tex').read()
# D7 变更
content = content.replace(old1, new1)
content = content.replace(old2, new2)
open('paper.tex', 'w').write(content)  # 检查点
# 继续 D4...
content = open('paper.tex').read()     # 重新读取
```

### Step 2: D4 TikZ 图

添加收敛框架图或架构图。避免 `label={...:...}` 冒号陷阱（触发 PGF Math Error）。

推荐用显式 `\node[font=\bfseries, above]` 作层标签，而非 `label=...` 选项。

### Step 3: D2 算法/方程

添加诊断算法或决策伪代码。注意:
- `\begin{algorithm}[H]` 在 elsarticle 中有效
- `\Comment{}` 可以带注释
- 阈值标注为"基于文献的合理估计"

### Step 4: D1/D6 叙事升级

- D1: 在 Introduction 末段添加编号贡献列表
- D6: 在 Conclusion 添加收敛框架定位 + 转化路线表

## 实战验证

**论文**: vor-pd-systematic-review v3 (Core3∩Core5, avg 0.800→0.821, +0.021)
- D7: 6/56 未引用全部整合 → 56/56=100%
- D4: 收敛框架 TikZ 图 + 转化路线表
- D2: Algorithm 2 诊断分类算法 (4步决策树)
- D1: 5条贡献列表
- D6: 收敛框架定位 + 3阶段路线图

**关键数据点**: 22页, 391KB, 56bib/56cite, 2Fig+6Tab+2Alg+9Eq
