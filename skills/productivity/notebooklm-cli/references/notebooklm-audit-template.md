# NotebookLM Audit Report Template

Generate this report after auditing a NotebookLM knowledge base.

## Template

```markdown
# 📚 NotebookLM 审计报告

> 生成时间: {DATE}
> 笔记本总数: {N}

## 📊 总体概况

| 指标 | 值 |
|:----|:---|
| 笔记本总数 | {N} |
| 所有者 | {M} ({Pct}%) |
| 共享 | {K} ({Pct2}%) |
| 最早创建 | {DATE_EARLIEST} |
| 最近创建 | {DATE_LATEST} |

## 📁 主题分类

```
{Category 1}    ████████████████  {N}  ({Pct}%)
{Category 2}    ████████████████  {N}  ({Pct}%)
...
```

## 📄 关键笔记本来源质量

### ⭐ {Notebook Name}（{Owner Type}）
**来源数**: {N}
- 📄 PDF: {N}
- 📝 Markdown: {N}
- 🌐 Web Page: {N}
- 年代跨度: {RANGE}
- 状态: all ready / some stale

## 🔗 跨笔记本关联图谱

```
{ASCII art graph showing connections}
```

## ⚠️ 发现的问题

| 严重度 | 问题 | 涉及笔记本 | 建议 |
|:------|:----|:----------|:-----|
| 🔴 高 | ... | ... | ... |
| 🟡 中 | ... | ... | ... |
| 🟢 低 | ... | ... | ... |

## 🎯 行动建议

### P0 - 立即执行
1. ...

### P1 - 近期优化
1. ...

### P2 - 常规维护
1. ...
```
