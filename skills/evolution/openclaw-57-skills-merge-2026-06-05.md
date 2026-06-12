# OpenClaw 57 Skills Merge Record

> 吸收日期: 2026-06-05
> 源: openclaw/openclaw (376,897⭐, MIT)
> 验证: 同源 SKILL.md 范式，130K⭐ Claude Code 也验证相同哲学

## 技能分类与映射

### messaging (6): discord, imsg, slack, telegram, wacli, xurl
### productivity (9): 1password, apple-notes, apple-reminders, bear-notes, taskflow, taskflow-inbox-triage, things-mac, tmux, trello
### research (10): blogwatcher, gemini, gh-issues, himalaya, model-usage, nano-pdf, openai-whisper, openai-whisper-api, oracle, summarize
### creative (7): canvas, gifgrep, meme-maker, sherpa-onnx-tts, songsee, video-frames, voice-call
### devtools (7): coding-agent, healthcheck, node-inspect-debugger, python-debugpy, session-logs, skill-creator, spike
### social (4): camsnap, discord, slack, spotify-player
### hardware (4): blucli, gog, openhue, sonoscli
### utility (10): clawhub, diagram-maker, eightctl, github, goplaces, mcporter, node-connect, ordercli, peekaboo, sag

## 重叠技能 (6个)

| 技能 | 决策 | 原因 |
|:-----|:-----|:-----|
| blogwatcher | KEEP Synthos | 5391B > 1414B，Synthos更完整 |
| notion | KEEP Synthos | 5536B > 3864B，Synthos更完整 |
| obsidian | KEEP Synthos | 6081B > 2939B，Synthos更完整 |
| node-inspect-debugger | MERGE OC | 246B << 3573B，合并OpenClaw → 3781B |
| python-debugpy | MERGE OC | 295B << 2552B，合并OpenClaw → 2727B |
| spike | MERGE OC | 210B << 1888B，合并OpenClaw → 2028B |

## 验证

- 所有57个技能的SKILL.md均经过手动检查
- 格式归一化为 Synthos 规范 (YAML frontmatter → 文言 → 白话 → 触发条件 → 验证清单)
- 重复的 allowed-tools 和 metadata 字段已标准化
- 5个方法论吸收 (autocontext, PaperDebugger, 724-office, Claude Code, OpenClaw) 与57个技能互补
