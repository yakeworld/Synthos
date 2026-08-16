---
name: tool-registry
category: tool
description: Synthos 工具注册表 — 成熟脚本/CLI 精确契约、调用优先级、违规模式
version: 1.0.0
---

# Synthos 工具注册表

> **工程层**：本文档只定义"调什么工具、怎么调"的事实契约。
> 何时调、为何调、路由决策见上层 `task-router/SKILL.md`（哲学层）。

## 调用优先级（L0-L3）

```
L0 不重新造轮子: skill 库 → 成熟脚本 → 成功案例 → 自己写
L1 能调用:       skill 非空 / 非 redirect stub / 路径存在 / CLI 参数正确
L2 执行稳定:     可复现 / 参数已验证 / 同一输入同一输出
L3 成功优先:     调成熟脚本 > 读代码再实现 > 从头写
```

**铁律**：调成熟脚本 > 读代码后再实现 > 自己从头写。先调通最小用例再扩展。

## 工具清单（Synthos 已知成熟工具）

| 工具 | 用途 | 契约要点 |
|------|------|---------|
| `jabkit-rs fetch` | 学术检索（26 源） | `--provider=<源> --query="<关键词>" --porcelain`，25s 内出 BibTeX。S2 已修复。详见 knowledge-acquisition/tools/jabkit-rs.md |
| `literature.py` | PDF 下载 + 管线编排 | 检索用 jabkit-rs，**literature.py 仅下载**。支持 `--sources` 多源 |
| `paper-manager/download_one.py` | 单篇下载 | 成熟脚本，勿重写 |
| `doi-fetch` | PDF 下载唯一入口 | 4 层降级。详见 knowledge-acquisition/tools/doi-fetch.md |
| `lit-import` | BibTeX 去重入库 | `--library <bib> --download-pdf <dir>` |
| `scihub-link-scan.py` | 链接可用性扫描 | 不下载，仅检查 |

## 违规模式（禁止）

- ❌ 写 `batch_pipeline_v1~v5` 系列，每次重新实现下载逻辑 → 应直接调 `literature.py`
- ❌ 子任务读了现有脚本但没调用，自己写 wget → 应直接 `python3 existing_script.py`
- ❌ 7 源检索写成自定义 API 调用 → 应直接用 `literature.py --sources ...`
- ❌ 批量处理写 Python 脚本逐篇调 API → 每篇独立调太慢，用成熟管线
- ❌ 只查 `.bbl` 不查内联 `thebibliography` → 两种引用格式都要处理

## 执行纪律

- 子 Agent 找不到 ACQ skill 时，fallback 到 `literature search` CLI 命令
- `delegate_task` 的 context 传空串，不传微操指令——子 Agent 有自己的 SOUL.md + 技能库
- 检查 tool_trace 中 terminal 是否执行了成熟脚本（评估子 Agent 是否"调了成熟脚本还是自己写实现"）
- 脚本路径存在、CLI 参数正确是调用前置条件（L1）
