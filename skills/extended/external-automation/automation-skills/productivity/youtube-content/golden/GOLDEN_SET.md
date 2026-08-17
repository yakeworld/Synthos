---
name: youtube-content
description: Golden set — YouTube 转录获取与内容转换
---

# 金测集 · youtube-content

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 输入/输出样本位于 `cases/` 与 `expected/`，一一对应。

## 测试用例

| ID | 场景 | 基因 | 关键检查 | case | expected |
|----|------|------|---------|------|----------|
| case_001 | 正常路径：标准 watch URL 获取转录并生成摘要 | YOUT-001 | `extract_video_id` 从 `youtube.com/watch?v=` 提取 11 位 ID；转录非空；未指定格式时默认输出 5-10 句摘要 | `cases/case_001.json` | `expected/case_001.json` |
| case_002 | 错误路径：视频转录被禁用 | YOUT-004 | API 返回 disabled → 输出 `{"error": "Transcripts are disabled for this video."}` 且退出码 1；向用户说明并建议检查字幕页 | `cases/case_002.json` | `expected/case_002.json` |

## 覆盖的基因

- **YOUT-001** 默认摘要 — case_001
- **YOUT-004** 转录禁用告知 — case_002

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 备注

- 外部依赖 `youtube-transcript-api` 不可用时，验证走静态检查：仅校验 `extract_video_id` 与输出 schema，不发起网络请求。
- 时间戳格式：`H:MM:SS` 或 `M:SS`（见 `format_timestamp`）。
