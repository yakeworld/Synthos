# Batch Task Template — 批量任务编排模板

## 用于 quality-gate 的论文管线批量检查

### 任务格式

```json
{
  "id": 9,
  "paper": "COMPLETE-PAPERS",
  "issue": "d8_d10a_batch",
  "description": "完整管线6篇D8/D10a/DOI统一检查...",
  "papers": ["paper-a", "paper-b", "paper-c"],
  "priority": 2,
  "status": "pending"
}
```

### 批量处理规则

- 一次性处理 `papers` 数组中的所有论文
- 每篇执行 D8/D10a/DOI 检查后写入 07-quality/quality-report.md
- 完成后更新 progress.log，每篇一行
- 不拆分、不延迟
- **PARTIAL 论文特殊处理**：若批量任务包含 PARTIAL 论文，54/55 篇会因缺失 .bib 而 D8=0。这些论文不能执行 D8 扫描（无 bib 可匹配），但需要为每篇生成 07-quality/quality-report.md，明确记录"无 references.bib"问题。D8=0 不是计算错误，是管线状态的事实。
