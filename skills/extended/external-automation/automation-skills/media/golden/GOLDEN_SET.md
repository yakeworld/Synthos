---
name: media
description: media 金测集 — 父级路由索引的可执行测试
---

# 金测集: media

> 来源: SKILL.md「Golden 集合 · GOLDEN SET」+「验证清单 · VERIFICATION」。
> 本技能为父级路由索引（atom_type: parent-skill），不直接执行媒体操作；
> 每个 case 验证路由决策的正确性（P1 可复现性）与错误路径的合规处理（MEDI-003/MEDI-005）。

## 子技能清单（路由目标）

- `gif-search` — Tenor GIF 搜索与下载（creative）
- `heartmula` — HeartMuLa 开源音乐基础模型生成（creative）
- `songsee` — 音频频谱/多面板音频特征图生成（creative）
- `spotify` — Spotify 账号控制（creative）

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由 — GIF 搜索委托 gif-search | route=delegate, target=gif-search |
| case_002 | 正常路由 — 音乐生成委托 heartmula | route=delegate, target=heartmula |
| case_003 | 错误路径 — 请求落在 4 个子技能之外（视频剪辑） | route=reject, error 含上下文与恢复建议，不越级执行 |
| case_004 | 错误路径 — context 非 dict 违反 IO 契约 | route=reject, error=contract_violation |

## 通过标准

- 加权总分 ≥ 0.80（critical 项必过）
- case_001/002: route 必须为 delegate，target 必须精确命中上表子技能名，无越级直接执行（验证清单 L70）
- case_003/004: 必须拒绝（route=reject），错误信息必须包含上下文与恢复指引，不得静默失败（MEDI-005）
- expected/ 与 cases/ 文件数量与命名一一对应（case_001..case_004）

## 权重

| 权重 | 值 | 用例 | 含义 |
|------|----|------|------|
| critical | 1.0 | case_001, case_003 | 正常路由命中 / 越界请求拒绝（核心判别） |
| high | 0.7 | case_002, case_004 | 次级路由 / 契约校验错误路径 |

## 关联

- SKILL.md Genes: MEDI-001 ~ MEDI-006
- SKILL.md 验证清单: 5 项 checkbox（契约输入 / 4子技能可路由 / 正确路由无越级 / 原子边界精确 / 输出结构一致）
- 方法论: golden-test-methodology（GOLD-001/002/003）
