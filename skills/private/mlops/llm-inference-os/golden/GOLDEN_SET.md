---
name: llm-inference-os
description: GOLDEN_SET.md
---

# 金测集: llm-inference-os

> 单一真理来源。所有改进必须通过 golden 测试。
> 语义依据：SKILL.md「Golden 集合 · GOLDEN SET」「Genes (LLM-001..LLM-007)」「验证清单 · VERIFICATION」「示例 · EXAMPLES」。

## 测试用例
| ID | 类型 | 描述 | 关键检查（gene 映射） |
|----|------|------|----------------------|
| case_001 | 正常路径 | 用户请求「用 Qwen3-VL 在 Linux (Ubuntu/Debian) 高并发部署推理集群」 | LLM-001（VL 后缀=多模态）、LLM-003（平台评级）、LLM-004（内核调优 20-30%）、LLM-005（结论可溯源）、LLM-006（步骤可重放） |
| case_002 | 错误路径 | 用户请求「用 Qwen3.5 跑图片分类」 | LLM-001（无 VL 后缀 → 纯文本，拒绝图片任务）、LLM-002（推荐 Qwen2.5-VL/Qwen3-VL）、错误信息含上下文与恢复建议 |
| case_003 | 正常路径（边界） | 在 Windows 原生 + macOS 各部署一套 vLLM 推理节点 | LLM-003（弃用 Windows 原生/ macOS，迁移至 Ubuntu/Debian ⭐⭐⭐⭐⭐）、LLM-006（迁移步骤逐步重放结果一致） |

## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过（一票否决）
- 错误路径（case_002）必须拒绝非法请求，不得执行图片任务，且错误信息含上下文背景与恢复建议（RULES 异常约束）

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（型号判定、平台选择、拒绝非法多模态请求） |
| high | 0.7 | 重要但不致命（内核调优实测、结论可溯源） |
| medium | 0.4 | 有价值但不是核心（推荐型号记录在案、重放验证） |
