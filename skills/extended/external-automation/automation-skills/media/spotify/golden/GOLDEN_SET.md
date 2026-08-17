name: spotify
description: spotify 金测集 — Hermes Spotify 7 工具集（播放/搜索/播放列表/库）的最小调用序列与失败路径可执行测试
---

# 金测集: spotify

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (SPOT-001~007) + Critical failure modes。
> 本技能通过 Hermes Spotify 工具集（7 工具：playback/devices/queue/search/playlists/albums/library）
> 控制用户 Spotify 账号。核心纪律：**最小化工具调用**（canonical patterns）与
> **失败不盲目重试**（SPOT-004：403 类错误立即停止并告知用户）。
> 每个 case 验证工具调用序列的正确性与错误处理路径（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：播放指定专辑 "play miles davis kind of blue" | 恰好 2 次调用：`spotify_search(types=["album"], limit=1)` → `spotify_playback(action="play", context_uri=<album_uri>)`（SPOT-001）；无 get_state 预检、无搜索结果描述 |
| case_002 | 正常：把当前歌曲加入私有播放列表 "Late Night Jazz" | 恰好 3 次调用：`spotify_playlists list`（按名找 id，SPOT-006）→ `get_currently_playing`（单调用取 track uri，SPOT-005：204 视为无播放）→ `spotify_playlists add_items`（playlist_id + uris） |
| case_003 | 错误路径："pause" 但无活跃设备 | `pause` 返回 403 No active device → 停止重试（retry_count == 0）；可选 `spotify_devices list` 确认为空；提示用户先启动 Spotify 客户端 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 调用序列必须精确为 2 步（search → play），context_uri 使用专辑类型化 URI；禁止循环描述搜索结果、禁止 get_state 预检（"What NOT to do"）
- case_002: 找用户私有播放列表必须走 `spotify_playlists list`，严禁 `spotify_search`（SPOT-006）；`get_currently_playing` 仅单次调用；add_items 的 uris 为 track URI 数组
- case_003: 必须零重试（403 No active device 为永久错误，SPOT-004）；输出必须含"先启动 Spotify 客户端 + 任意播放一轨 + 再重试"的用户指引；禁止盲目重试

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 工具调用序列 / 错误处理结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 调用序列按工具名+action 精确匹配，顺序敏感，次数精确
- URI 类型必须与动作匹配（context_uri 接受 album/playlist/artist；uris 为 track URI 数组）
- 错误路径必须同时含 stop_retry（零重试）与 user_guidance（含恢复建议，RULES 异常约束）

## 关联

- SKILL.md Genes: SPOT-001~007
- SKILL.md 验证清单: 5 项（活跃设备 / Premium / URI 类型一致 / 私有播放列表与 204 / 429 与 401）
- SKILL.md Critical failure modes: 403 No active device、403 Premium required、204 No Content、429、401
- SKILL.md 示例: 示例 1（播放专辑）、示例 2（加入播放列表）、示例 3（无活跃设备）
