# NotebookLM Audit Workflow Reference

## Quick Reference — Chinese Medical Research Keyword Map

```python
CATEGORIES = {
    "ADHD/眼动追踪": ["ADHD", "眼动", "eye tracking", "eyetracking", "注视", "扫视"],
    "前庭/VOR/BPPV": ["VOR", "前庭", "BPPV", "眩晕", "耳石", "vestibular"],
    "眼科/虹膜/3D眼球": ["眼", "虹膜", "iris", "瞳孔", "pupil", "角膜", "eyeball", "ocul"],
    "AI/ML/编程": ["AI", "ML", "机器学习", "深度", "神经网", "OpenCode", "智能体", "agent", "编程", "Python"],
    "NSFC/基金/项目申报": ["NSFC", "国自然", "基金", "标书", "申报", "英才计划", "重点实验室"],
    "教学/课程": ["教学", "课程", "教案", "培养", "AIGC", "通识"],
    "科研方法论/论文写作": ["CRISP", "TRIPOD", "论文写作", "科研设计", "可解释", "可信"],
    "专利/知识产权": ["专利", "知识产权"],
    "医院管理/报告": ["医院", "报告", "奖励", "创新门诊", "绩效"],
}
```

## Source Quality Scoring Rubric

| Dimension | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
|-----------|--------|--------|--------|--------|
| Quantity | 20+ sources | 10-19 | 3-9 | 1-2 |
| Type diversity | 4+ types | 3 types | 2 types | 1 type |
| Freshness | ≤1 month old | ≤6 months | ≤1 year | >1 year |
| Status | 100% ready | ≥80% ready | ≥50% ready | <50% ready |
| Naming | All standard | Most standard | Mixed | Uninformative |

## Report Template Sections

1. 总体概况 (total count, owner/shared, date range)
2. 主题分类 (category bars + count per category)
3. 关键笔记本来源质量评估 (per-notebook 5-dimension rating)
4. 跨笔记本关联图谱 (ASCII art graph)
5. 发现的问题 (🔴/🟡/🟢 table)
6. 来源类型分布 (PDF vs Markdown vs DOCX vs etc.)
7. 行动建议 (P0/P1/P2 priorities)

## Pitfalls from Practice

- `notebooklm list --json` output may truncate long titles — use the full id for `notebooklm use`
- Iterating through 70+ notebooks one-by-one takes ~15 min. Categorize first, then spot-check key notebooks only.
- Private audit reports MUST go to `~/notebooklm-audit/` or similar, NOT into public project `docs/`
