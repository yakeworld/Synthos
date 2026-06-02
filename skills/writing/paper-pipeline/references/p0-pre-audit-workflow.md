# P0 前置审计 (Pre-Audit)

在开始论文写作前，检查本地磁盘是否存在同主题已完成的论文，避免重复劳动。

## 执行步骤

### 1. 搜索已有产出

```bash
# 在 projects/ 和 outputs/ 目录搜索
find . -name "*.tex" | xargs grep -il "关键词" 2>/dev/null
find . -name "*.pdf" | xargs grep -il "关键词" 2>/dev/null

# 或使用 search_files 工具
search_files(pattern="关键词", file_glob="*.{tex,pdf,bib,md}", path=".")
```

### 2. 快速审计已存在论文

| 检查项 | 方法 |
|:-------|:-----|
| 同数据集论文 | grep 数据集名称 |
| 同类方法论文 | grep 方法关键词 |
| 同目标变量 | grep 预测目标 |

### 3. 判定

- **0 结果** → ✅ 无重复，可以开工
- **有结果但不同方法/视角** → 标记为 Related Work，进入 P-1
- **有结果且完全重叠** → 🔴 STOP，与用户确认是否需要在已有基础上迭代

## 常见审计关键词

| 领域 | 搜索关键词 |
|:-----|:-----------|
| Pima糖尿病 | pima, diabetes prediction, PIDD |
| PD吸入性肺炎 | dysphagia, aspiration, Parkinson |
| 眼动追踪 | eye tracking, pupil, VOR, nystagmus |
