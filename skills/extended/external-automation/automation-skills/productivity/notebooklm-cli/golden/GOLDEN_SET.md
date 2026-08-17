---
name: notebooklm-cli
description: notebooklm-cli 金测集 — NotebookLM CLI 知识大脑的可执行测试
---

# 金测集: notebooklm-cli

> 来源: SKILL.md Golden 集合 + 关键陷阱 + Genes (NOTE-001~007) + IO_CONTRACT。
> 核心能力：通过 `notebooklm` CLI 操作 NotebookLM（Tier 1 知识大脑）— 项目/源管理、
> 逐问法 Q&A、内容生成（report/video/audio/slide-deck/infographic）。
> IO_CONTRACT: input `action: str, params: dict` → output `result: dict`。
> 每个 case 验证命令选择、超时/上传陷阱处理与降级路径（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：纯英文逐问法 Q&A | `notebooklm ask "..."` 超时 ≥90s（NOTE-002）；Prompt 为纯英文 ASCII 规避 confusable 扫描（NOTE-004）；同一项目串行提问（NOTE-001） |
| case_002 | 正常：PDF 源上传前文本层预检 | `pdftotext file.pdf - \| wc -c` 检查（NOTE-003）；≈0 字符时改 arXiv URL 直传或 `--type text` 文本上传；上传后 `source list` 验证状态（NOTE-007） |
| case_003 | 错误路径：Google 服务不可达 | `notebooklm list` 抛 `httpx.ConnectTimeout`、curl 000 → 触发 Manual Fallback（NOTE-006）：`pdftotext` 提取全文做五维人工评估，阈值不变（≥0.85=T1） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 命令为 `notebooklm ask "<english prompt>"`；timeout 配置 ≥90s；Prompt 不含中文字符；同一项目无并行 ask；结果以 dict 返回且回答完整（30-60s 响应未截断）
- case_002: 上传前必须执行 `pdftotext <pdf> - | wc -c` 预检；文本层 <1000 chars 的文件不得直接 `source add file.pdf`，改 arXiv URL 或 `--type text`；上传后立即 `source list` 复核，status=error 时回退文本上传，空列表时重试 2-3 次（NOTE-007）
- case_003: 检测到 `httpx.ConnectTimeout` 后须先诊断（curl notebooklm.google.com 与 httpbin.org 对比），确认 Google 被阻断后走 Manual Fallback；报告保存至 `<paper-dir>/07-quality/layer-b-report.md`，评分阈值与在线版一致
- 所有 case: Markdown 上传走 `source add "$(cat file.md)" --type text` 且先剥离 YAML frontmatter（NOTE-005）；>80KB 内容用 Python subprocess 而非 shell 参数

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 命令 / 结果结构 / 降级路径结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 命令按 SKILL.md 快速参考表精确结构匹配，参数值可不同
- 结果必须是 dict，键名稳定（`status`, `answer`/`sources`, `fallback` 等）
- 错误路径必须同时含 `error` 上下文与 `recovery`/`fallback` 建议两个字段（异常约束）

## 关联

- SKILL.md Genes: NOTE-001~007
- SKILL.md 关键陷阱: 14 项（ipynb 400 / symlink / ask 超时 / frontmatter / 无文本层 / 并行串话 / storage state / 安全扫描 / 网络不可达 等）
- 相关技能: knowledge-extraction（EXT 原子）, knowledge-base-audit, markitdown-convert（MD 供上传）
