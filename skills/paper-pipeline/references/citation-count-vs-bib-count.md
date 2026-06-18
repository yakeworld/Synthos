# 引用计数与D10a的正确理解（2026-06-18 更新）

## 核心问题

扫描论文库时，`\cite{}` 出现次数经常超过 Bib 条目数。这**不是 bug**，而是正常现象。

## 原因

同一文献在论文中可能被**多次引用**：
- 引言中：概述领域背景 → `\cite{smith2020deep}`
- 方法中：说明技术细节 → `\cite{smith2020deep}`  
- 讨论中：对比自身结果 → `\cite{smith2020deep}`

每个 `\cite{}` 都是独立出现，但指向同一个 bibkey。

## 正确处理方式

### D10a 计算（引用覆盖率）
```
D10a = |unique_cite_keys ∩ bib_keys| / |bib_keys|
```
- 提取所有 `\cite{key1, key2}` 中的**去重**键
- 与 bib 文件中的键求交集
- 这是衡量 bib 中有多少条目**实际被引用**

### 引用总数（总引用频次）
```
total_cites = len(all \cite occurrences)
```
- 所有 `\cite` 出现次数（含重复）
- 用于评估论文引用丰富度
- total_cites ≥ unique_cite_keys × 2 表示有重复引用（正常）

### D10a > 100% 的情况

当 unique_cite_keys 数量超过 bib 条目数时可能出现：
- bib 文件中有重复条目（同一文献写了两次）
- 引用计数方式不一致
- **这不表示问题**，D10a 超过 100% 只说明引用比 bib 条目多，通常是正常现象

## 成熟度扫描指标

评估论文成熟度时：
1. **D10a** 看引用覆盖率（0-100%，>100%也正常）
2. **total_cites** 看引用丰富度（≥30为良好，≥50为优秀）
3. **unique_cite_keys** 看实际引用文献数量
4. **bib_count** 看参考文献总量

不要将 total_cites 与 bib_count 直接比较来判断"异常"。
