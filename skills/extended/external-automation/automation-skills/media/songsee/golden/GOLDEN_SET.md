name: songsee
description: songsee 金测集 — 音频频谱可视化（spectrogram/mel/chroma 等多面板）的正常与错误路径可执行测试
---

# 金测集: songsee

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (SONG-001~006)。
> 本技能通过 Go CLI `songsee`（`go install github.com/steipete/songsee/cmd/songsee@latest`）
> 从 WAV/MP3 音频生成频谱与多面板音频特征可视化图像。
> 每个 case 验证 CLI 参数构造、输出验证清单的执行正确性（P1 可复现性、P0 证据可溯性：
> 输出文件存在且非零字节可独立复核）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：多面板特征网格（调试合成） | `--viz spectrogram,mel,chroma,tempogram,flux` 多类型 → 单图 5 面板网格（SONG-001）；输出 png 存在非零字节；`--style` 色板合法（SONG-006） |
| case_002 | 正常：时间切片局部分析 | `--start 12.5 --duration 8` 切片不越界（12.5+8 ≤ 音频时长）（SONG-002）；输出 jpg 存在非零字节 |
| case_003 | 错误路径：非法 `--viz` 类型 | viz 值不在 9 类合法集合内 → 拒绝执行，结构化错误含上下文 + ≥2 条恢复建议（RULES 异常约束），不生成输出文件 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: viz 列表必须为合法 9 类（spectrogram/mel/chroma/hpss/selfsim/loudness/tempogram/mfcc/flux）的子集；输出图像存在且非零字节，`--format` 与实际扩展名一致
- case_002: 必须先行确认切片区间 `[start, start+duration]` 落在音频实际时长内（越界即失败）；输出仅含指定时间段
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"参数回声 + 失败上下文（哪个参数非法）+ ≥2 条恢复建议"，禁止生成任何输出文件、禁止静默降级

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 执行结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 合法 viz 类型集合精确匹配 9 类之一（验证清单第 3 项）
- 输出文件断言 = 存在 + 非零字节 + 扩展名与 `--format` 一致
- 错误路径必须同时含 context 与 recovery 两个字段（RULES 异常约束：错误信息含上下文和恢复建议）

## 关联

- SKILL.md Genes: SONG-001~006
- SKILL.md 验证清单: 6 项（Go 安装 / 输入格式 / viz 合法性 / 切片越界 / 输出非零字节 / vision_analyze 可辨）
- SKILL.md 示例: 例 2（多面板网格）、例 3（时间切片）
