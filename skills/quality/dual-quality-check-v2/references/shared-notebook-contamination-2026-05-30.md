# Shared NotebookLM 源文件污染 — 2026-05-30 实战

**论文**: pima-crispdm (Process-Driven Credibility: A CRISP-DM Helix Framework)
**NotebookLM 项目 ID**: 8e1174cd (Shared 类型)

## 问题

上传论文 PDF 到 Shared NotebookLM 项目做 Layer B (Gemini) 7维评审时，Gemini 的回答中引用了不属于当前论文的源文件内容。

### 具体表现

1. Gemini 回答中提到 "源自 `家庭与童年教育` 等整合文献库" — 这是另一个完全不相关的 NotebookLM 项目
2. D6 (新颖性) 评分为 **0.98** — 明显偏高（正常应为 0.70-0.75），说明 Gemini 被项目中其他不相关源文件的内容"污染"，误判了论文的新颖性
3. 修复建议中提到了不属于该论文的文献 key（如 `AlBayati2025Role`、`Gupta2024Diabetes`、`Marlisa2024APPLICATION`）

## 根因分析

Shared NotebookLM 项目是其他用户共享的，其中包含了大量不相关的源文件。当论文 PDF 被上传到这个 Shared 项目后，Gemini 在进行全局上下文分析时，把项目中其他不相关源文件的内容也纳入了评分依据。

**关键因素**:
- Shared 项目无法用 CLI 删除旧 Source（`source delete` 在 Shared 项目中是伪成功）
- Shared 项目的 Source 数量多、内容杂（该项目中包含大量不同论文的参考文献）
- Gemini 的 D6 评分基于对整个 Notebook 的理解，而非仅限当前对话中的新上传文件

## 影响

| 维度 | 应有评分 | 实际评分 | Δ |
|:-----|:--------:|:--------:|:-:|
| D6 新颖性 | 0.70-0.75 | 0.98 | +0.23~0.28 |

这导致校准后分数虚高，掩盖了论文的实际短板。

## 检测方法

1. 检查 Gemini 回答中是否引用不相关的论文/项目名称
2. 对异常偏高的评分（尤其是 D6 新颖性），使用 `source list` 查看项目中是否有不相关源文件
3. 用 `grep` 检查 Gemini 回答中是否出现本项目之外的文献 key

## 修复方法

1. **Owner 项目**: 清理不相关 Source，或创建一个干净的专有项目
2. **Shared 项目**: 无法清理 Source，改用 Owner 项目或上传到干净的 Notebook
3. **最佳实践**: 为每篇论文创建专属的 Owner Notebook（不要用 Shared 项目做质量评审）

## 对比

| 项目类型 | Layer B Gemini 评审可靠性 | Source 管理能力 |
|:---------|:--------------------------|:---------------|
| **Owner 项目** | ✅ 高 | ✅ 可清理/删除 |
| **Shared 项目** | ❌ 可能被污染 | ❌ `source delete` 伪成功 |

## 结论

做 Layer B (Gemini) 论文质量评审时，**必须使用 Owner 权限的 NotebookLM 项目**。Shared 项目的源文件污染会导致 D6 评分异常偏高，校准分失实。如果只有 Shared 项目可用，D6 评分应下调 0.20-0.30 作为污染修正。
