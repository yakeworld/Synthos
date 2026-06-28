---
name: automation-skills
description: "**触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---





## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Batch Quality Score Extraction

**触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。

## 背景

Synthos 管线中，每篇论文的 `01-manuscript/step_quality_check.md` 包含一个 JSON 块，其中 `score` 字段有多种格式。
批量处理时必须处理所有格式变体，且需要清理 LaTeX 反斜杠才能解析 JSON。

## 步骤

1. **列出目标论文目录** — 从 paper-queue.json 获取批次列表
2. **逐篇定位 `step_quality_check.md`** — 使用 `os.walk()` 查找，因为文件可能在不同子目录
3. **清理 LaTeX 反斜杠** — 在 `json.loads()` 之前移除所有非法 `\X` 转义
4. **提取分数** — 根据格式类型映射到 0-100 范围
5. **写入 state.json** — 更新 `quality_score` 字段，设置 `gate_status`

## 分数格式映射

| 格式 | 提取逻辑 | 示例 |
|------|---------|------|
| `score`(number) + `max_score` | `score / max_score * 100` | 2.5/10 → 25 |
| `score`(dict) + `total_score` | `total_score * 10` | 7.8 → 78 |
| `overall_score`(number) | `overall_score * 10` | 6.5 → 65 |
| `detailed_scores`(dict) | `avg(vals) / max(vals) * 100` | 均值/最大值 → 百分比 |
| 纯文本（如

  io_contract: input: ['paper_dirs: list[str] -> scores: dict', 'output: ['scores: dict (paper_name: quality_score, extraction_errors: list[str])]']


# Batch Quality Score Extraction

**触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。

## 背景

Synthos 管线中，每篇论文的 `01-manuscript/step_quality_check.md` 包含一个 JSON 块，其中 `score` 字段有多种格式。
批量处理时必须处理所有格式变体，且需要清理 LaTeX 反斜杠才能解析 JSON。

## 步骤

1. **列出目标论文目录** — 从 paper-queue.json 获取批次列表
2. **逐篇定位 `step_quality_check.md`** — 使用 `os.walk()` 查找，因为文件可能在不同子目录
3. **清理 LaTeX 反斜杠** — 在 `json.loads()` 之前移除所有非法 `\X` 转义
4. **提取分数** — 根据格式类型映射到 0-100 范围
5. **写入 state.json** — 更新 `quality_score` 字段，设置 `gate_status`

## 分数格式映射

| 格式 | 提取逻辑 | 示例 |
|------|---------|------|
| `score`(number) + `max_score` | `score / max_score * 100` | 2.5/10 → 25 |
| `score`(dict) + `total_score` | `total_score * 10` | 7.8 → 78 |
| `overall_score`(number) | `overall_score * 10` | 6.5 → 65 |
| `detailed_scores`(dict) | `avg(vals) / max(vals) * 100` | 均值/最大值 → 百分比 |
| 纯文本（如
metadata:
  synthos:
    priority: P2
    atom_type: tool
    description: 批量处理论文 step_quality_check.md 中的 quality_score 并写入 state.json。
    signature: 'paper_dirs: list[str] -> scores: dict'
    related_skills: [quality-gate, paper-pipeline, paper-references-scanning, research-paper-search]
---



# Batch Quality Score Extraction

**触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。

## 背景

Synthos 管线中，每篇论文的 `01-manuscript/step_quality_check.md` 包含一个 JSON 块，其中 `score` 字段有多种格式。
批量处理时必须处理所有格式变体，且需要清理 LaTeX 反斜杠才能解析 JSON。

## 步骤

1. **列出目标论文目录** — 从 paper-queue.json 获取批次列表
2. **逐篇定位 `step_quality_check.md`** — 使用 `os.walk()` 查找，因为文件可能在不同子目录
3. **清理 LaTeX 反斜杠** — 在 `json.loads()` 之前移除所有非法 `\X` 转义
4. **提取分数** — 根据格式类型映射到 0-100 范围
5. **写入 state.json** — 更新 `quality_score` 字段，设置 `gate_status`

## 分数格式映射

| 格式 | 提取逻辑 | 示例 |
|------|---------|------|
| `score`(number) + `max_score` | `score / max_score * 100` | 2.5/10 → 25 |
| `score`(dict) + `total_score` | `total_score * 10` | 7.8 → 78 |
| `overall_score`(number) | `overall_score * 10` | 6.5 → 65 |
| `detailed_scores`(dict) | `avg(vals) / max(vals) * 100` | 均值/最大值 → 百分比 |
| 纯文本（如 "T1 QUALIFIED"） | 人工判断 90+ | QUALIFIED → 95 |

## LaTeX 反斜杠清理代码

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

## 陷阱

### 论文目录命名不一致
尝试变体：`name`, `name.replace('_','-')`, `f'paper-{name}'` 等。

### 文件位置不固定
`step_quality_check.md` 可能在 `01-manuscript/`、`07-quality/`、根目录等。
必须使用 `os.walk()` 查找。

### 已处理过的论文跳过
检查 `state.json` 中是否已有 `quality_score`，避免重复写入。

### 批量处理的超时
34 篇论文可能超时。建议分批次（10-15 篇/批），每批一个 queue item。

## 相关

- `references/latex-escape-json-parsing-fix.md` (research-paper-search) — 完整的 LaTeX 清理代码和已知影响论文清单
- `references/gate-batch-processing-pattern.md` (quality-gate) — G1-G7 批处理模式
- paper-pipeline — 管线整体编排
- quality-gate — G1-G7 闸门定义

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
