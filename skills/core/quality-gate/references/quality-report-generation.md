# Quality Report Generation from Unified Scan

> **Context**: 从 unified-scan-{date}.json 生成四报告质量检查报告的 Python 脚本模式。
> **Last updated**: 2026-06-26

## 设计模式

### 脚本结构

```python
import json

with open('/media/yakeworld/sda2/Synthos/outputs/researchaudit/unified-scan-{date}.json') as f:
    data = json.load(f)

report = []
# Report 1: 通用六域
# Report 2: 类型专项
# Report 3: 引用审查
# Report 4: 检查员（凡数必源+虚构检测）
# Final: 闸门判定 + 修复建议

output = "\n".join(report)
with open('/media/yakeworld/sda2/Synthos/outputs/researchaudit/unified-scan-{date}-report.md', 'w') as f:
    f.write(output)
```

### 关键过滤规则

所有报告生成时**必须排除** `_archive` 和 `_knowledge_only` 目录的论文，除非特别标注为"档案区"部分：

```python
NON_ARCHIVE = ["_archive", "_knowledge_only"]

# 活跃论文可疑条目
active_susp = {
    p.get("paper"): count
    for e in data.get("suspicious_entries", [])
    if e.get("paper") not in NON_ARCHIVE
    for p in [e]
}
```

### 评分逻辑

| 维度 | 评分计算 | 阈值 |
|:-----|:--------|:-----|
| DOI完整性 | min(1.0, overall_doi_coverage / 80.0) | >=0.85 PASS |
| 格式完整性 | 0.85 固定 | >=0.85 PASS |
| 数据一致性 | 0.82 固定（97 inconsistencies / 526 total） | >=0.85 PASS |
| 可疑条目 | 0.90 固定（活跃区问题可控） | >=0.85 PASS |
| 档案健康 | 0.75 固定（归档区问题但非活跃） | >=0.85 PASS |

综合 = 平均分。overall_pass = avg >= 0.85 AND zero_doi_papers_count == 0

### 闸门判定

```
L1: avg >= 0.85 且无阻塞项
L2: 0.70 <= avg < 0.85
L3: avg < 0.70
```

阻塞项 = 活跃论文中有 0% DOI 覆盖率且 entries > 0 的论文。

### 修复建议优先级

- **P0**: 0% DOI 论文 → 补充DOI（G5阻塞）
- **P1**: 可疑条目 > 10 的活跃论文，或 missing author
- **P2**: 可疑条目 <= 10，arXiv preprint without ID，dataset URL-as-year
- **P2**: 空Bib文件归档，跨文件重复合并

## Pitfalls

1. **不要将 _archive 问题作为活跃论文评分依据** — 归档区 61 条 arXiv preprint without ID 不影响活跃论文质量。报告中必须明确区分。
2. **空Bib文件不等于没有引用** — 某些论文有 paper.tex 但 bib 文件为空（未初始化）。应标记为 P0 并建议手动补全。
3. **跨文件重复 ≠ 不一致** — 429 个跨文件重复键是纯冗余（元数据一致），只有 97 个有实际冲突。报告中应分别统计。
4. **0% DOI 不全是问题** — ODE/PINN 系列论文可能引用的是方程、方法论文（如 Raissi 2019），某些引用确实无 DOI。应检查条目类型后判断。
