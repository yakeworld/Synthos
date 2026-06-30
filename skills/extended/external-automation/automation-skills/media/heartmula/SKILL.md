---
name: heartmula
description: "HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Generates full songs from lyrics + tags. Comparable to Suno for open-source. Includes:"
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


# HeartMuLa - Open-Source Music Generation

## Overview
HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Generates full songs from lyrics + tags. Comparable to Suno for open-source. Includes:
- **HeartMuLa** - Music language model (3B/7B) for generation from lyrics + tags
- **HeartCodec** - 12.5Hz music codec for high-fidelity audio reconstruction
- **HeartTranscriptor** - Whisper-based lyrics transcription
- **HeartCLAP** - Audio-text alignment model

## When to Use
- User wants to generate music/songs from text descriptions
- User wants an open-source Suno alternative
- User wants local/offline music generation
- User asks about HeartMuLa, heartlib, or AI music generation

## Hardware Requirements
- **Minimum**: 8GB VRAM with `--lazy_load true` (loads/unloads models sequentially)
- **Recommended**: 16GB+ VRAM for comfortable single-GPU usage
- **Multi-GPU**: Use `--mula_device cuda:0 --codec_device cuda:1` to split across GPUs
- 3B model with lazy_load peaks at ~6.2GB VRAM

## Installation Steps

### 1. Clone Repository
```bash
cd ~/  # or desired directory
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
```

### 2. Create Virtual Environment (Python 3.10 required)
```bash
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
```

### 3. Fix Dependency Compatibility Issues

**IMPORTANT**: As of Feb 2026, the pinned dependencies have conflicts with newer packages. Apply these fixes:

```bash
# Upgrade datasets (old version incompatible with current pyarrow)
uv pip install --upgrade datasets

# Upgrade transformers (needed for huggingface-hub 1.x compatibility)
uv pip install --upgrade transformers
```

### 4. Patch Source Code (Required for transformers 5.x)

**Patch 1 - RoPE cache fix** in `src/heartlib/heartmula/modeling_heartmula.py`:

In the `setup_caches` method of the `HeartMuLa` class, add RoPE reinitialization after the `reset_caches` try/except block and before the `with device:` block:

```python
# Re-initialize RoPE caches that were skipped during meta-device loading
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**Why**: `from_pretrained` creates model on meta device first; `Llama3ScaledRoPE.rope_init()` skips cache building on meta tensors, then never rebuilds after weights are loaded to real device.

**Patch 2 - HeartCodec loading fix** in `src/heartlib/pipelines/music_generation.py`:

Add `ignore_mismatched_sizes=True` to ALL `HeartCodec.from_pretrained()` calls (there are 2: the eager load in `__init__` and the lazy load in the `codec` property).

**Why**: VQ codebook `initted` buffers have shape `[1]` in checkpoint vs `[]` in model. Same data, just scalar vs 0-d tensor. Safe to ignore.

### 5. Download Model Checkpoints
```bash
cd heartlib  # project root
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

All 3 can be downloaded in parallel. Total size is several GB.

## GPU / CUDA

HeartMuLa uses CUDA by default (`--mula_device cuda --codec_device cuda`). No extra setup needed if the user has an NVIDIA GPU with PyTorch CUDA support installed.

- The installed `torch==2.4.1` includes CUDA 12.1 support out of the box
- `torchtune` may report version `0.4.0+cpu` — this is just package metadata, it still uses CUDA via PyTorch
- To verify GPU is being used, look for "CUDA memory" lines in the output (e.g. "CUDA memory before unloading: 6.20 GB")
- **No GPU?** You can run on CPU with `--mula_device cpu --codec_device cpu`, but expect generation to be **extremely slow** (potentially 30-60+ minutes for a single song vs ~4 minutes on GPU). CPU mode also requires significant RAM (~12GB+ free). If the user has no NVIDIA GPU, recommend using a cloud GPU service (Google Colab free tier with T4, Lambda Labs, etc.) or the online demo at https://heartmula.github.io/ instead.

## Usage

### Basic Generation
```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### Input Formatting

**Tags** (comma-separated, no spaces):
```
piano,happy,wedding,synthesizer,romantic
```
or
```
rock,energetic,guitar,drums,male-vocal
```

**Lyrics** (use bracketed structural tags):
```
[Intro]

[Verse]
Your lyrics here...

[Chorus]
Chorus lyrics...

[Bridge]
Bridge lyrics...

[Outro]
```

### Key Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length in ms (240s = 4 min) |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temperature |
| `--cfg_scale` | 1.5 | Classifier-free guidance scale |
| `--lazy_load` | false | Load/unload models on demand (saves VRAM) |
| `--mula_dtype` | bfloat16 | Dtype for HeartMuLa (bf16 recommended) |
| `--codec_dtype` | float32 | Dtype for HeartCodec (fp32 recommended for quality) |

### Performance
- RTF (Real-Time Factor) ≈ 1.0 — a 4-minute song takes ~4 minutes to generate
- Output: MP3, 48kHz stereo, 128kbps

## Pitfalls
1. **Do NOT use bf16 for HeartCodec** — degrades audio quality. Use fp32 (default).
2. **Tags may be ignored** — known issue (#90). Lyrics tend to dominate; experiment with tag ordering.
3. **Triton not available on macOS** — Linux/CUDA only for GPU acceleration.
4. **RTX 5080 incompatibility** reported in upstream issues.
5. The dependency pin conflicts require the manual upgrades and patches described above.

## Links
- Repo: https://github.com/HeartMuLa/heartlib
- Models: https://huggingface.co/HeartMuLa
- Paper: https://arxiv.org/abs/2601.10547
- License: Apache-2.0

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


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



# Heartmula

