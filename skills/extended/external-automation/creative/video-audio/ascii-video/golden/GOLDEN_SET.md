---
name: ascii-video
description: GOLDEN_SET.md
---

# 金测集: ascii-video

> 来源: SKILL.md Genes ASCI-001~007 + 验证清单 + 6-stage Pipeline 架构 + Creative Standard。
> 语义判定: 视频渲染无确定性像素输出，golden 校验的是**流程契约**（模式选择、6 阶段管线完整性、创意概念前置、亮度检查、陷阱规避、逐场景差异化、输出规格），而非具体画面。
> P1 可复现性: 同一 input 必须产生符合 expected 结构约束的执行计划/输出元数据（效果选择可不同，管线结构与验证步骤必须一致）。

## 设计依据

核心契约（来自 SKILL.md）:
1. **创意概念前置**（ASCI-001）: 编码前必须阐述创意概念（mood/visual story/color world/"what makes THIS different"），拒绝提示词字面转录
2. **6 阶段管线**（Pipeline Architecture）: `INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE`，每模式必须走完
3. **6 种模式**（Modes 表）: video-to-ascii / audio-reactive / generative / hybrid / lyrics / TTS narration，input 类型必须匹配 mode
4. **亮度用 tonemap()**（Critical Implementation Notes + 验证清单第 2 条）: 关键帧先单帧测试，`canvas.mean() > 8`，禁用 `canvas * N` 线性乘子
5. **逐场景差异化**（ASCI-006）: 每场景不同 background effect / palette / color strategy / shader 强度，禁止全片同一配置
6. **统一美学**（ASCI-004）: 全片共享色温/字符调色板/运动词汇
7. **catalog 之外发明**（ASCI-003/007）: 至少 1 个自定义元素 + 1 个用户未要求的视觉时刻
8. **已知陷阱规避**（验证清单第 5 条）: macOS 用 `font.getmetrics()`、ffmpeg 不 `stderr=subprocess.PIPE`、初始化验证字体兼容性
9. **输出规格**（Step 2 技术设计）: 默认 1920x1080@24fps MP4；首帧即达视觉惊艳标准（ASCI-002）
10. 输入校验失败（文件不存在/格式不支持）→ 结构化错误（约束规则第 1/3 条）

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常: audio-reactive 音乐可视化（lo-fi chill 45s 音频） | mode == audio-reactive; 6 阶段管线完整; creative_concept 非空; test_frames_first + brightness > 8 + tonemap (非乘子); 逐场景差异化配置; 1 个 catalog 外发明; 输出 1920x1080@24fps MP4 |
| case_002 | 错误路径: 输入视频文件不存在 | 返回结构化错误（error_type/context/recovery 非空）; 不启动管线（pipeline_stages_executed == 0）; 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `mode == "audio-reactive"`；`pipeline_stages` 完整含全部 6 阶段且顺序正确；`creative_concept` 五个子字段（mood/visual_story/color_world/character_texture/uniqueness）非空；`pre_render_verification` 含 test_frames_at_timestamps 且 brightness_threshold > 8 且 brightness_method == "tonemap"（非 linear_multiplier）；`per_scene_variation` 覆盖 ≥3 场景且各场景 config 不完全相同；`invented_elements` ≥ 1；`output` 含 1920x1080 / 24fps / MP4；陷阱规避三项（font_getmetrics / ffmpeg_no_stderr_pipe / font_compat_validation）均为 true
- case_002: `error` 非空且含 `error_type`（input_file_missing）、`context`、`recovery`；`pipeline_stages_executed == 0`；`crash == false`

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（管线完整性 / 错误路径结构化 / 亮度检查方法正确） |
| high | 0.7 | 创意概念前置、逐场景差异化、输出规格 |
| medium | 0.4 | catalog 外发明、陷阱规避、统一美学 |

## 关联

- SKILL.md Genes: ASCI-001~007
- 管线: SKILL.md § Pipeline Architecture (INPUT→ANALYZE→SCENE_FN→TONEMAP→SHADE→ENCODE)
- 模式表: SKILL.md § Modes（6 种）
- 验证清单: SKILL.md § 验证清单 · VERIFICATION
- 陷阱: SKILL.md § Critical Implementation Notes
- IO_CONTRACT: `request: str, context: dict -> result: dict`

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-02 | 初始金测集，2 个 case（audio-reactive 正常路径 + 缺失输入错误路径） | Synthos Agent |
