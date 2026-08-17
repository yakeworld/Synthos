---
name: pixel-art
description: pixel-art 金测集 — 照片→复古像素艺术 PNG / MP4 的可执行测试
---

# 金测集: pixel-art

> 来源: SKILL.md 验证清单 + Genes (PIXE-001~007) + 工作流/预设目录/陷阱。
> 技能签名: `pixel_art(in, out, preset=..., palette=..., block=...)` → PNG；
> `pixel_art_video(in, out, scene=..., duration=..., fps=..., seed=..., export_gif=...)` → MP4(/GIF)。
> 每个 case 验证像素化与动画管道的输入校验、参数语义、输出可验证性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：标准照片 → NES 预设像素化 PNG | preset 键名精确（大小写敏感）；输出 PNG 存在且颜色数 ≤ NES 54 色；像素块为 8px（PIXE-004/005） |
| case_002 | 正常路径：像素化 PNG → night 场景 MP4（seed 固定） | MP4 可被 ffprobe 打开且非零大小；场景为 night；seed=42 固定保证可复现 |
| case_003 | 错误路径：源图宽度 <100px 且未预放大，block=8 | 触发陷阱（<100px 大块坍缩）→ 结构化错误含上下文+恢复建议（先放大源图），不静默产出坍缩图（PIXE-005） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 输出 PNG 存在于指定路径，`Image.open(p).getcolors()` 颜色数 ≤ 54（NES 硬件调色板），无插值模糊
- case_002: `ffprobe` 可打开 MP4 且文件大小非零；duration≈6s、fps≈15 与入参一致
- case_003: 必须拒绝直接转换 —— 错误信息含"请求回声 + 触发条件（源宽 <100px × block 8）+ 恢复建议（先 upscale 源图）"，禁止仅返回通用错误

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 像素化/动画结果或错误结构
- `verification`: 可执行的校验断言列表（getcolors / ffprobe / 参数回显）

期望输出采用**语义等价判定**：
- 预设键名必须精确匹配预设目录（14 选 1，大小写敏感）
- 错误路径必须同时含 context 与 recovery 两个字段
- 单色/双色调色板（mono_green / mono_amber）必须强制 `color=0.0` 去饱和（PIXE-006）

## 关联

- SKILL.md Genes: PIXE-001~007
- SKILL.md 验证清单: 6 项（PNG 生成+block 一致 / 颜色数匹配 / 硬件调色板键名 / MP4 ffprobe 校验 / <100px 预放大 / 单色去饱和）
- 脚本: `scripts/pixel_art.py`, `scripts/pixel_art_video.py`, `scripts/palettes.py`
