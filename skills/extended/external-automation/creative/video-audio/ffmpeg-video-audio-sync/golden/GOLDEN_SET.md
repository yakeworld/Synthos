---
name: ffmpeg-video-audio-sync
description: GOLDEN_SET.md
---

# 金测集: ffmpeg-video-audio-sync

> 来源: SKILL.md Genes FFMP-001~007 + 验证清单 + Quick Reference + Debugging Checklist。
> 语义判定: golden 校验的是**诊断与修复命令序列**（ffprobe 校验、正确 ffmpeg 命令选择、陷阱规避），而非视频像素内容。
> P1 可复现性: 同一 input（含 ffprobe 探测结果）必须产生符合 expected 的诊断结论与修复命令（命令参数必须结构一致，路径可不同）。

## 设计依据

核心契约（来自 SKILL.md）:
1. **时长不一致**（FFMP-001）: 合并前 ffprobe 对比 v:0/a:0 时长，较长流用 `-t` **显式裁剪**，不得仅依赖 `-shortest`
2. **音频格式标准化**（FFMP-002）: 非标准音频（采样率≠44100 / 非立体声）合并前先转 AAC 44100Hz stereo 192kbps
3. **MP4 拼接走 TS 中间格式**（FFMP-003/005）: `-c copy` 转 TS → 二进制 `cat` → 重编码 MP4；**禁止**对 `start_time` 全为 0 的分段直接 `-f concat -c copy`（PTS 冲突静默丢段）
4. **源分段 preset ≥ medium**（FFMP-004）: `ultrafast`/`fast` 编码的源 MP4 转 TS 时静默丢 ~25% 数据，必须用 `-preset medium` 或更高
5. **视频短于旁白**（FFMP-006）: `-stream_loop -1` + `-shortest` 循环视频匹配音频
6. **最终校验**（FFMP-007）: ffprobe 对比 v:0 与 a:0 duration，差值 < 0.2s；拼接后总时长 = 各分段之和，nb_frames 总和 = 分段帧数之和
7. 输入校验失败（文件不存在/无流）→ 结构化错误（约束规则第 1/3 条）

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常: 3 段 MP4 拼接 + 旁白同步（视频 116.3s < 音频 128s, 源为 ultrafast 编码, 音频 48kHz 单声道） | 诊断识别 3 个陷阱: preset<medium / 拼接需 TS 路径 / 时长需 stream_loop; 修复命令序列结构正确（重编码源分段→TS→cat→MP4→stream_loop+shortest→ffprobe 终检 <0.2s） |
| case_002 | 错误路径: 视频文件不存在 | 返回结构化错误（error_type/context/recovery 非空）; 不执行任何 ffmpeg 命令; 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `diagnosis` 含全部 3 个陷阱（source_preset_too_fast / concat_requires_ts_path / video_shorter_than_audio）；`fix_plan` 命令序列按 expected 的 stage 顺序完整（每 stage 关键参数匹配: 重编码 `-preset medium`、TS 转换 `-c copy -f mpegts`、二进制 `cat`、`-stream_loop -1` + `-shortest`）；`final_verification` 含 ffprobe v:0/a:0 duration 对比且 tolerance_s < 0.2
- case_002: `error` 非空且含 `error_type`（input_file_missing）、`context`、`recovery`；`ffmpeg_commands_executed == 0`；`crash == false`

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（陷阱全部识别 / 修复命令关键参数 / 错误路径结构化） |
| high | 0.7 | 诊断命令（ffprobe）先行、最终校验 <0.2s |
| medium | 0.4 | 命令序列 stage 完整、恢复建议完备 |

## 关联

- SKILL.md Genes: FFMP-001~007
- 三大陷阱: SKILL.md § Quick Reference（Duration / Sample Rate / MP4 Concatenation）
- 静默丢段: SKILL.md § MP4 Concatenation Pitfall（v1.2）+ § MP4→TS Conversion Data Loss
- 验证清单: SKILL.md § 验证清单 · VERIFICATION
- IO_CONTRACT: `video_file: str, audio_file: str -> synced_output: str`

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 占位金测集（单 case 模板） | Synthos Agent |
| 0.2.0 | 2026-07-02 | 重写为语义化金测集，2 个 case（多陷阱正常路径 + 缺失输入错误路径） | Synthos Agent |
