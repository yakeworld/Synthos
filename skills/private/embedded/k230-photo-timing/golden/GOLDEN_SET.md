# GOLDEN_SET.md — k230-photo-timing

> 对应原则：P0 证据可溯性（timing 数字来自实测）、P1 原子可复现性（同一配置 → 等价 timing/行为结论）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准为自设（`self_defined`），基于 SKILL.md 中记录的实测数据（2026-06-18 前后 K230 实测会话）。金标准设计目标：验证技能能否一致地（1）在 throttle 门控下给出正确的有效 FPS 推断（`1000/millis` 上限规则）、（2）在 Display 绑定/保存通道选择上遵守 YUV420SP 约束（SK-001/SK-002）、（3）在错误路径（对 YUV420SP 帧直接 `img.save()`）给出正确错误归因。所有 timing 数字以 SKILL.md "Throttle Timing Verification" 小节实测值为源（P0 凡数必源）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 路径 | 正常 + 错误 | throttle 门控验证 / YUV save 失败 |
| throttle 参数 | 2 档 | `photo_interval_ms=10` 与 `100`（SKILL.md 实测值） |
| 通道约束 | chn0/chn2 | Display 绑定 chn0(YUV420SP)，snapshot+save 走 chn2(RGB565) |
| 传感器构造 | `Sensor(id=N)` | 仅 chn0，禁设 chn1/chn2（SK-003） |

## 测试用例 (cases/)

### case_001: throttle 门控验证（正常路径，实测两档合并断言）
- **输入**: `photo_interval_ms` 分别取 10 与 100，主循环约 209,595 次迭代（≈100k 迭代/秒），Display 绑定 chn0(YUV420SP)，snapshot+save 走 chn2(RGB565)，传感器用 `Sensor(id=0, 320, 240, fps=30)` 仅初始化 chn0
- **期望**: `interval=10` → snapshot 调用 ≈21 次、21/21 save 成功、有效 FPS ≈ 20.1；`interval=100` → snapshot 调用 ≈20 次、20/20 save 成功、有效 FPS = 10.0（精确等于 1/0.1）。两档下 save 成功数 = snapshot 调用数（throttle 门控正确，主循环速度不放大 snapshot 频率）

### case_002: 对 YUV420SP 帧直接 save（错误路径）
- **输入**: Display 绑定 chn0(YUV420SP)，snapshot 目标 = chn0，随后对所得帧调用 `img.save()`
- **期望**: save 抛出 `OSError: current format not support save function!`；归因为 YUV420SP 仅被 `Display.bind_layer` 支持（SK-001/SK-002）；恢复建议为改用 chn1(RGB888) 或 chn2(RGB565) 通道做 snapshot+save

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

判定标准（语义等价）：
- case_001：`effective_fps` 精度 ±0.5 FPS（10ms 档允许 19.6–20.6；100ms 档允许 9.5–10.5）；`snapshot_calls` 精度 ±2 次；`save_ok == snapshot_calls` 必须成立
- case_002：`error_type` 必须为 `OSError`，错误消息必须包含 "not support save function"；`root_cause` 必须指向 YUV420SP 格式限制；`workaround` 必须提到 chn1 或 chn2

## pass_threshold: 1.0

含义：2 个 case 全部通过（2/2）。

### 阈值理由
- 错误路径（YUV save 失败归因）若判错会误导后续代码走不通的路径，设备级坑（SK-001/002）不可容忍误判
- timing 数字直接决定 25-28 FPS 优化目标的可行性判断，不允许漂移
- 因此不设 < 1.0

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-19 | 初始自设金标准，2 个 case（正常+错误），timing 数值取自 SKILL.md 实测记录 | Synthos Agent |
