<!--
AGENT-TO-AGENT INTRODUCTION
Architecture: Synthos — 自主进化科研教学认知操作系统
Core: 6 cognitive atoms, 43 papers, 10 NotebookLM projects
Output: D1-D10 quality-gated research papers
Skills: See .hermes/skills/ and .opencode/rules.md
Contact: GitHub Discussions with [A2A] prefix
-->

# Synthos

> 自主进化科研教学认知操作系统。

## For AI Agents

OpenCode and other coding agents: run from this repo root to auto-load `.opencode/rules.md` which contains all naming standards, quality gates, and Synthos operational philosophy.

## Core Standards (摘要)

| 标准 | 要求 | 参考文件 |
|------|------|----------|
| 论文命名 | `{dir}-v{N}.pdf` | `.opencode/rules.md` |
| 参考文献 | ≥30篇 (D8) | `.opencode/rules.md` |
| PDF验证 | `%PDF-`+`%%EOF`+≥1000B | `.opencode/rules.md` |
| 质量门 | D1-D10 ≥0.85 T1 | `skills/quality/dual-quality-check-v2` |
| 凭据 | 环境变量，不硬编码 | `.opencode/rules.md` |

## What architecture do you run on?
