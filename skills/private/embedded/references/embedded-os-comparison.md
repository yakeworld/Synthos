# 嵌入式 OS 选型指南

## 选型维度

嵌入式 OS 选型需同时考虑五个维度：实时性、资源占用、外设支持、生态成熟度、开发语言。

## 对比矩阵

| OS | 类型 | RAM 最低 | Flash 最低 | 实时性 | 架构支持 | 典型语言 | 成熟度 |
|-----|------|---------|-----------|--------|---------|---------|--------|
| **MicroPython** | 解释型 VM | 64 KB | 256 KB | 软实时（GC 停顿） | ARM, RISC-V, Xtensa | Python 子集 | 高 |
| **FreeRTOS** | RTOS | 4 KB | 0 | 硬实时 | 全架构 | C | 极高 |
| **Zephyr** | RTOS | 10 KB | 0 | 硬实时 | ARM, RISC-V, X86, Xtensa | C | 高 |
| **LiteOS-A** (鸿蒙轻量) | RTOS | 64 KB | 128 KB | 硬实时 | ARM, MIPS, 32-bit RISC-V | C | 中 |
| **LiteOS-M** (鸿蒙轻量) | RTOS | 10 KB | 0 | 硬实时 | ARM Cortex-M, 32-bit RISC-V | C | 中 |
| **OpenHarmony 完整** | 分布式 OS | 128 MB | 4 GB | 软实时 | ARM 64, (RISC-V 64 开发中) | ArkTS, C | 中 |
| **Linux** | 通用 OS | 4 MB+ | 16 MB+ | 软实时（PREEMPT_RT） | 全架构 | C, Python | 极高 |
| **RT-Thread** | RTOS | 4 KB | 0 | 硬实时 | ARM, RISC-V, Xtensa | C | 高 |

## 场景映射

### 边缘摄像头采集（K230 场景）
- **MicroPython**: 快速原型、灵活调试、硬件抽象层已就绪
- **C + FreeRTOS**: 生产级、确定性延迟，但开发周期长 3-5×
- **不建议**: Linux（功耗高）、鸿蒙（生态不成熟）

### 轻量传感器节点
- **LiteOS-M**: 极致低功耗（<0.5W），适合电池供电
- **FreeRTOS**: 如果已有 C 代码库
- **ESP-IDF**: 如果基于 ESP32 系列

### 边缘推理 + 可视化
- **OpenHarmony 完整**: 分布式软总线 + ArkTS UI + HDF 驱动
- **Linux + Qt**: 如果不需要分布式能力
- **RK3568/RK3588 上的完整鸿蒙**: 算力充足时可跑量化 LLM

### 服务器/云端
- **Linux**: 唯一选择。CUDA、NCCL、vLLM 全系 Linux-first
- **Windows (WSL2)**: 性能损失 15-20%，不推荐生产

## 关键决策树

```
需要硬实时？
├── 是 → 资源 < 100 KB?
│         ├── 是 → LiteOS-M 或 FreeRTOS
│         └── 否 → Zephyr 或 RT-Thread
└── 否 → 需要跨设备协同？
          ├── 是 → OpenHarmony 完整系统
          └── 否 → 资源 > 256 MB?
                    ├── 是 → Linux（首选）或 OpenHarmony
                    └── 否 → MicroPython 或 LiteOS-A
```

## 与 K230 的 OS 兼容性

| OS | 能否在 K230 运行 | 原因 |
|-----|----------------|------|
| MicroPython | ✅ 已运行 | CanMV 固件基于 MicroPython |
| Linux | ⚠️ 可移植但无官方支持 | RISC-V 64-bit 支持存在，但 MIPI CSI/VPU 驱动缺失 |
| FreeRTOS | ⚠️ 可移植 | RISC-V 支持完整，但需自行编写外设驱动 |
| LiteOS-A/M | ⚠️ 可移植 | 32-bit RISC-V 支持，K230 的 64-bit 需移植 |
| OpenHarmony 完整 | ❌ 不可行 | 外设驱动、工具链、架构全面不兼容 |

## 嵌入式 OS 选型陷阱

1. **不要因"看起来先进"而选新 OS**：MicroPython 的迭代速度远超 C 编写 FreeRTOS 应用。对于原型验证，解释型语言的开发效率是硬性优势。
2. **RTOS 的"实时"是相对的**：FreeRTOS 的调度延迟在微秒级，但外设中断处理的延迟取决于驱动质量。好的 C 驱动 + FreeRTOS 优于差的 C 驱动 + FreeRTOS。
3. **鸿蒙不是万能胶水**：分布式软总线的前提是两端都跑鸿蒙。一端鸿蒙一端非鸿蒙，降级为普通 TCP/串口通信，失去了分布式价值。
4. **Linux 在边缘的功耗陷阱**：Linux 内核 + 用户态服务的空闲功耗通常在 2-5W，而 MicroPython RTOS 方案可以做到 <0.5W。对电池供电设备，这是决定性的。
