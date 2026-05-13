# IO_CONTRACT.md — gap-discovery

## 输入
- `literature`: 文献列表（from knowledge-extraction），至少5篇
- `focus`: 研究焦点/领域（可选，用于限制空白发现范围）

## 输出
```json
{
  "gaps": [
    {
      "id": "G001",
      "type": "contradiction|methodology_gap|unanswered_question|outdated_evidence",
      "statement": "空白描述",
      "source_refs": ["论文A", "论文B"],
      "priority": "P0|P1|P2|P3",
      "rationale": "为什么这是重要空白"
    }
  ],
  "metadata": {
    "literature_analyzed": 10,
    "gaps_found": 3,
    "focus_area": "optional"
  }
}
```

## 质量要求
- 每5篇文献至少发现1个空白
- 空白必须有至少2篇文献支撑
- 空白类型必须明确分类
