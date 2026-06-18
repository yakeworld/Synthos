# step_quality_check.md JSON 解析 — LaTeX 反斜杠陷阱

**触发条件**: 读取 `01-manuscript/step_quality_check.md` 或其他 `step_*.md` 文件时，文件中包含的 JSON 块内有 LaTeX 数学表达式（如 `$\sigma$`），导致 Python `json.loads()` 报 `Invalid \escape`。

## 原因

Python JSON 仅允许 8 种合法转义：`\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX`。
LaTeX 中的 `$\sigma$`、`$E(t)$`、`$\varepsilon$` 等在 JSON 字符串值内变为 `\sigma`、`E(t)`、`\varepsilon`，这些是非法转义。

## 修复代码

```python
import json

def clean_json_for_latex(content):
    """Parse JSON from content containing LaTeX backslash escapes."""
    start = content.find('{')
    end = content.rfind('}') + 1
    if start < 0:
        raise ValueError("No JSON block found")
    json_str = content[start:end]

    result = []
    i = 0
    while i < len(json_str):
        if json_str[i] == '\\':
            if i + 1 < len(json_str) and json_str[i+1] in '"\\bfnrtu/':
                result.append(json_str[i:i+2])
                i += 2
            elif i + 1 < len(json_str) and json_str[i+1] == 'u':
                result.append(json_str[i:i+6])
                i += 6
            else:
                result.append(json_str[i+1])  # \sigma -> sigma
                i += 2
        else:
            result.append(json_str[i])
            i += 1
    return json.loads(''.join(result))
```

## 已知影响论文（v88 — 2026-06-11）

以下论文在 `step_quality_check.md` 中出现此问题：

| 论文 | 分数格式 | 修复后得分 |
|------|---------|-----------|
| optokinetic-reflex-pinn | score=dict + total_score | 78 |
| endolymph-hydropressure-ode | overall_score | 65 |
| dual-ellipse-pupil-localization | score=2.5, max_score=10 | 25 |
| data-leakage-breast-cancer-critical-audit | score=dict, detailed_scores | 75 |
| diplopia-binocular-fusion-ODE | detailed_scores | 65 |
| paper-95-nystagmus-PINN | score=dict | 0 |
| vhit-pinn-ode | total_score | 72 |
| Paper_100_fixation-vernier-PINN | detailed_scores | 72 |
| Paper_101_optokinetic-reflex-PINN | detailed_scores | 65 |
| 137-ciliary-body-ODE | detailed_scores | 45 |
| 148-corneal-epithelial-wound-healing-ODE | detailed_scores | 0 |
| 151-ocular-torsion-dynamics-ODE | detailed_scores | 0 |
| 152-intraocular-pressure-rhythm-ODE | detailed_scores | 65 |
| 3wd-framework-trustworthy-clinical-ai | detailed_scores | 0 |
| orthokeratology-corneal-remodeling-ODE-paper-117 | detailed_scores | 0 |

## 其他文件格式变体

某些 `step_quality_check.md` 使用不同分数格式：
- `score` + `max_score`：标准数值格式（2.5/10 → 25）
- `score` (dict) + `total_score`：复合分数（total_score=7.8 → 78）
- `overall_score`：单一分数（6.5 → 65）
- `detailed_scores` (dict)：平均分/最大值 → 百分比
- 纯文本（如 "T1 QUALIFIED"）：需人工判断为 90+
