---
name: songsee
description: songsee
version: 1.0.0
category: creative
signature: 'songsee -> creative: Generate spectrograms and multi-panel audio feature
  visualizations from audio fi'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# songsee

Generate spectrograms and multi-panel audio feature visualizations from audio files.

## Prerequisites

Requires [Go](https://go.dev/doc/install):
```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

Optional: `ffmpeg` for formats beyond WAV/MP3.

## Quick Start

```bash
# Basic spectrogram
songsee track.mp3

# Save to specific file
songsee track.mp3 -o spectrogram.png

# Multi-panel visualization grid
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Time slice (start at 12.5s, 8s duration)
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg

# From stdin
cat track.mp3 | songsee - --format png -o out.png
```

## Visualization Types

Use `--viz` with comma-separated values:

| Type | Description |
|------|-------------|
| `spectrogram` | Standard frequency spectrogram |
| `mel` | Mel-scaled spectrogram |
| `chroma` | Pitch class distribution |
| `hpss` | Harmonic/percussive separation |
| `selfsim` | Self-similarity matrix |
| `loudness` | Loudness over time |
| `tempogram` | Tempo estimation |
| `mfcc` | Mel-frequency cepstral coefficients |
| `flux` | Spectral flux (onset detection) |

Multiple `--viz` types render as a grid in a single image.

## Common Flags

| Flag | Description |
|------|-------------|
| `--viz` | Visualization types (comma-separated) |
| `--style` | Color palette: `classic`, `magma`, `inferno`, `viridis`, `gray` |
| `--width` / `--height` | Output image dimensions |
| `--window` / `--hop` | FFT window and hop size |
| `--min-freq` / `--max-freq` | Frequency range filter |
| `--start` / `--duration` | Time slice of the audio |
| `--format` | Output format: `jpg` or `png` |
| `-o` | Output file path |

## Notes

- WAV and MP3 are decoded natively; other formats require `ffmpeg`
- Output images can be inspected with `vision_analyze` for automated audio analysis
- Useful for comparing audio outputs, debugging synthesis, or documenting audio processing pipelines

## 验证清单 · VERIFICATION

- [ ] Go 已安装且 `songsee` 可通过 `go install ...@latest` 正常执行
- [ ] 输入音频文件存在且格式受支持（WAV/MP3 原生解码；其他格式已安装 `ffmpeg`）
- [ ] `--viz` 值为合法可视化类型（spectrogram/mel/chroma/hpss/selfsim/loudness/tempogram/mfcc/flux），多类型生成网格图
- [ ] `--start`/`--duration` 时间切片在音频实际时长范围内，未越界
- [ ] 输出图像文件存在且非零字节，格式为指定 `--format`（jpg/png）
- [ ] 输出图像可用 `vision_analyze` 读取，频谱内容清晰可辨

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Songsee

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[SONG-001]** 需要对比音频特征或调试合成时 → 使用 `--viz` 指定多种可视化类型（如 spectrogram, mel, chroma）以生成多面板网格图
- **[SONG-002]** 仅需分析音频特定片段时 → 使用 `--start` 和 `--duration` 参数截取时间切片进行局部可视化
- **[SONG-003]** 处理 WAV/MP3 以外的音频格式时 → 确保系统已安装 `ffmpeg` 以支持原生解码之外的格式转换
- **[SONG-004]** 需要自动化分析音频内容时 → 将生成的可视化图像作为输入传递给 `vision_analyze` 进行视觉特征提取
- **[SONG-005]** 需要调整频谱显示细节时 → 通过 `--window`、`--hop` 及 `--min-freq`/`--max-freq` 参数精细控制 FFT 窗口与频率范围
- **[SONG-006]** 需要标准化输出图像外观时 → 使用 `--style` 选择特定色板（如 magma, viridis）并指定 `--width`/`--height` 统一尺寸
