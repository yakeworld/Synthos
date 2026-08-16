---
name: k230-photo-timing
description: '**Result**: With Display binding, total `snapshot + save` should be ~35-40ms → **25-28 FPS** vs curr'
signature: 'k230-photo-timing -> embedded: synthetic skill for k230 photo timing'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**Result**: With Display binding, total `snapshot + save` should be ~35-40ms → **25-28 FPS** vs curr'
    signature: 'k230-photo-timing -> embedded: synthetic skill for k230 photo timing'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| Constructor | `Sensor()` default | `Sensor(id=0, w, h, fps)` |
| chn0 format | YUV420SP (Display) | RGB565 (save) |
| Display binding | bind chn0 to LAYER_VIDEO1 | No Display binding |
| chn1/chn2 | Set to RGB888/RGB565 | Not configured |
| snapshot() target | chn0 (YUV420SP) or chn2 (RGB565) | Default chn0 (RGB565) |
| Pipeline | Hardware (GDMA/DSP) | Pure software |
| snapshot time | **21ms** | **26-33ms** |

**Result**: With Display binding, total `snapshot + save` should be ~35-40ms → **25-28 FPS** vs current 20 FPS.

### YUV420SP Constraint

**YUV420SP is the ONLY format supported by Display.bind_layer.** Assert error:
```
AssertionError: bind video layer only support format PIXEL_FORMAT_YUV_SEMIPLANAR_420
```

YUV420SP cannot be saved via `img.save()` — `OSError: current format not support save function!`

The workaround is using chn1 (RGB888) or chn2 (RGB565/RGBP888) for snapshot+save operations.

## Multi-Sensor Rules

From `examples/17-Sensor/camera_dual_bind_hdmi.py`:

- Multiple sensors only need ONE `sensor.run()` call (any sensor's run() starts all)
- Multiple sensors all need `sensor.stop()` calls (each sensor must be stopped individually)
- Or call `Sensor.deinit()` once to stop all
- Comment warns: "当使用多个 Sensor 时，分辨率建议均设置为 1920 × 1080, 且 fps 设置为 30" — using other resolutions may cause display artifacts

## Throttle Timing Verification

Test with `photo_interval_ms = 10`:
- 209,595 main loop iterations → only 21 actual snapshot calls
- 21/21 save successful → throttle works correctly
- Effective FPS = 20.1 (limited by snapshot+save time, not by 1/0.01 = 100)

Test with `photo_interval_ms = 100`:
- 209,595 main loop iterations → 20 actual snapshot calls
- 20/20 save successful
- Effective FPS = 10.0 (exactly 1/0.1)

**Conclusion**: The throttle gate correctly limits to `1000/millis` calls regardless of main loop speed. Main loop runs at ~100,000 iterations/second, but only the gated calls execute snapshot.

## Empty Photo Directory Diagnosis

When `/data/320p_photos/` has multiple numbered directories but only one has files (e.g., 024 has 542 files, 025-034 are empty):

1. Check `/sdcard/photo_sequence.txt` — if it shows 34, then 34 sessions were initiated
2. Check if `photo_mode_start()` creates directory before sensor init — yes it does
3. Failed sessions still create directories but produce no files
4. Only sessions where ALL sensors initialize AND `current_mode == "photo"` AND `is_running == True` produce files

## New Pitfall: Directory Lifecycle After Serial Flood

**Root cause discovered 2026-06-18**: When main loop floods the serial port, `photo_mode_start()` may succeed in creating the directory (`ensure_dir()`) but the subsequent sensor init or camera run() call gets lost in the serial flood. The directory remains on SD card as an empty stub. This produces a cascade of empty directories (e.g., 025-034) with only the final successful run (024) containing actual photo files.

**Diagnosis pattern**:
- Directories exist but are empty → `ensure_dir()` ran, but sensor init failed (silently) or was interrupted
- Only one directory has files → all intermediate sessions failed to complete photo_mode_start()
- Directory with few files only on one camera → the other camera's init hung and triggered early stop

**Prevention**: Add a post-stop cleanup in `photo_mode_stop()` or a startup check that removes empty photo session directories older than N minutes. Consider:
```python
# In photo_mode_start(), before ensure_dir():
existing = [d for d in os.listdir(photo_dir) if os.path.isdir(os.path.join(photo_dir, d))]
for d in existing:
    full = os.path.join(photo_dir, d)
    try:
        files = os.listdir(full)
        if len(files) == 0:
            os.rmdir(full)  # Remove empty dir
    except:
        pass
```

## New Pitfall: REPL Window After rmmod Recovery

After `rmmod ftdi_sio; modprobe ftdi_sio`, the K230 serial port recovers BUT `main.py` continues flooding the UART with print statements. The first 2-3 seconds of REPL commands are often lost or garbled because:
- `main.py`'s `while True` loop has already been running since boot
- Thousands of print statements per second flood the 115200 baud serial buffer
- The device is NOT in a clean REPL state after driver reload — it's still executing `main.py`

**Recovery protocol**:
1. `sudo rmmod ftdi_sio; sleep 1; sudo modprobe ftdi_sio; sleep 1` — reload driver
2. Send 5-10x `Ctrl+C` to interrupt main loop
3. Send `Ctrl+D` to enter clean REPL
4. Send 1-2 `Ctrl+C` again to ensure clean `>>>` prompt
5. **Wait 0.5s** before sending the first useful command
6. If first command shows `...` continuation prompt, send Ctrl+C again

**Ampy is unreliable after recovery**: Use direct serial (`python3 -c "import serial..."`) for initial connectivity test, then switch to ampy for file operations once you have confirmed `>>>` prompt.

## K230 Device Recovery — Auto Serial Reset

When the K230 serial port becomes completely dead (all reads return empty, `ampy` hangs at rc=124), the serial driver (`ftdi_sio`) must be reloaded:

```bash
sudo rmmod ftdi_sio 2>/dev/null
sudo rmmod usb_serial 2>/dev/null
sleep 1
sudo modprobe ftdi_sio
sleep 1
```

After rmmod, the device may show `OSError: [Errno 5] Input/output error` on `in_waiting`. After modprobe, a simple `print("HI")` test confirms recovery.

This is NOT the same as a soft reset (Ctrl+D). The K230 can enter a state where the UART hardware is completely locked up — only the kernel driver reload restores it.

## K230 Sensor Multi-Channel Bug

**Critical limitation**: `Sensor(id=N, width, height, fps)` constructor + setting chn2 via `set_framesize(..., chn=2)` + `run()` **causes device hang**. Only single-channel init (chn0) works reliably with this constructor.

Both `Sensor()` default constructor + `set_framesize` + `set_framesize(..., chn=2)` + `run()` also hang.

**Workaround**: Only initialize and run chn0. Do NOT set chn1/chn2 when using `Sensor(id=N, ...)`. If multi-channel output is needed, use the official `Sensor()` default constructor without chn2, then use chn0 for everything.

**Evidence**: Both `Sensor(id=0, 320, 240, fps=30)` + chn2 set → hang AND `Sensor()` default + chn2 set → hang. The hang is immediate and unrecoverable without `rmmod ftdi_sio` + `modprobe ftdi_sio`.

## Related: Serial Flood → Silent Write Failure

When the K230 main loop floods the serial port (print statements, no throttling), ampy operations hang or timeout. **This compounds the silent-write problem:** you cannot verify the fix via ampy because the serial port is blocked. Debugging chain:

**Full session transcript with directory-lifecycle diagnosis**: references/serial-flood-empty-dir.md

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] Display 绑定通道（chn0）确认为 YUV420SP（`bind_layer` 唯一支持格式），且保存走 chn1/chn2（RGB888/RGB565）而非直接 `img.save()` YUV 帧
- [ ] 使用 `Sensor(id=N, ...)` 构造函数时仅初始化 chn0，未设置 chn1/chn2（否则设备立即挂起，需 rmmod 恢复）
- [ ] 多传感器场景：仅调用一次 `sensor.run()` 启动全部，且逐一 `sensor.stop()` 或统一 `Sensor.deinit()`
- [ ] Throttle 验证：`photo_interval_ms=10/100` 下主循环迭代数与有效 FPS 符合 `1000/millis`，save 成功数与 snapshot 调用数一致
- [ ] 空照片目录诊断：核对 `photo_sequence.txt` 会话数与有文件的目录数，区分静默初始化失败产生的空目录
- [ ] 串口无响应（ampy 挂起）时执行 `rmmod ftdi_sio` + `modprobe ftdi_sio` 重载驱动，而非仅软复位
- [ ] 驱动重载后按恢复协议进 REPL：多次 Ctrl+C → Ctrl+D → 再 Ctrl+C，等待 0.5s 后发首条命令，确认 `>>>` 提示符

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

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
> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
# K230 Photo Timing---
> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# K230 Photo Timing
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[SK-001]** 需要绑定 Display 层时 → 必须使用 YUV420SP 格式，因为这是 `bind_layer` 唯一支持的格式
- **[SK-002]** 需要保存图像文件时 → 必须使用 RGB565 或 RGB888 通道（chn1/chn2），因为 YUV420SP 不支持 `img.save()`
- **[SK-003]** 使用 `Sensor(id=N, ...)` 构造函数时 → 仅初始化 chn0 通道，禁止设置 chn1/chn2，否则会导致设备立即挂起
- **[SK-004]** 多传感器场景下 → 仅需调用一次 `sensor.run()` 启动所有传感器，但必须逐个调用 `sensor.stop()` 或统一调用 `Sensor.deinit()`
- **[SK-005]** 发现照片目录存在但为空时 → 检查 `photo_sequence.txt` 并清理空目录，以识别因串口阻塞导致的静默初始化失败
- **[SK-006]** 串口完全无响应（ampy 挂起）时 → 执行 `rmmod ftdi_sio` 和 `modprobe ftdi_sio` 重载内核驱动，而非仅发送软复位指令
- **[SK-007]** 驱动重载后进入 REPL 时 → 连续发送多次 Ctrl+C 和 Ctrl+D 以中断主循环并清除缓冲区，等待 0.5s 后再发送有效命令