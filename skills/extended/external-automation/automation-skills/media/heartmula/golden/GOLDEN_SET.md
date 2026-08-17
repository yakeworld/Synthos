# Golden Set — heartmula

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 技能核心：HeartMuLa 开源音乐生成（heartlib，Apache-2.0）——从 lyrics + tags 生成 MP3。
> 本集合覆盖：正常路径（GPU + lazy_load 生成）与错误路径（HeartCodec 误用 bf16 导致音质退化）。

## 测试用例表

| Case | 类型 | 输入摘要 | 预期 |
|------|------|----------|------|
| case_001 | 正常路径 · 生成 | Python 3.10 venv，3B 模型，`--lazy_load true`，`--codec_dtype float32`，结构标签歌词 + 无空格逗号 tags，`--max_audio_length_ms=240000` | 输出 MP3 存在且非零字节，48kHz 立体声 128kbps；日志出现 "CUDA memory" 行（峰值 ~6.2GB）；时长 ≤ 240s |
| case_002 | 错误路径 · codec dtype | `--codec_dtype bfloat16`（违反 HEAR-004） | 预检/验证阶段即被拦截：错误信息说明 HeartCodec 严禁 bf16（音质退化），要求改回 `float32`；不交付音质退化产物 |

## 通过标准

- **case_001**
  - [ ] venv 为 Python 3.10；datasets / transformers 已升级，RoPE 与 HeartCodec 两处补丁已应用
  - [ ] 3 个 checkpoint 位于 `./ckpt`（HeartMuLaGen、HeartMuLa-oss-3B、HeartCodec-oss）
  - [ ] 歌词使用括号结构标签（`[Verse]`/`[Chorus]` 等）；tags 为无空格逗号分隔（HEAR-006）
  - [ ] `--lazy_load true`，`--codec_dtype float32`（HEAR-001 / HEAR-004）
  - [ ] 输出 MP3 存在、非零字节、48kHz 立体声 128kbps，时长 ≤ `--max_audio_length_ms` / 1000 秒
  - [ ] 生成日志出现 "CUDA memory" 行（确认 GPU 被使用）
- **case_002**
  - [ ] 检测到 `--codec_dtype bfloat16` 即报错，不执行生成（或生成后验证门拒绝交付）
  - [ ] 错误信息包含上下文（违反的基因 HEAR-004 / 参数值）与恢复建议（`--codec_dtype float32`）
  - [ ] 不交付音质退化的 MP3（去形留神：交付可用产物而非中间产物）

## 复现命令

```bash
# 环境预检（验证清单）
python3 --version                     # 期望 3.10.x
ls ckpt/HeartMuLaGen ckpt/HeartMuLa-oss-3B ckpt/HeartCodec-oss
# case_001 生成
python ./examples/run_music_generation.py --model_path=./ckpt --version="3B" \
  --lyrics=./assets/lyrics.txt --tags=./assets/tags.txt \
  --save_path=./assets/output.mp3 --lazy_load true --codec_dtype float32
# 输出验证
file assets/output.mp3 && stat -c%s assets/output.mp3
# case_002 反例（应被拦截）
python ./examples/run_music_generation.py ... --codec_dtype bfloat16   # 期望：预检报错
```

> 注：RTF≈1.0，4 分钟歌曲约 4 分钟生成（GPU）。无 GPU/macOS 环境下推荐云端 GPU 或在线 Demo（HEAR-005），
> 该场景不属于本集合的交付断言。
