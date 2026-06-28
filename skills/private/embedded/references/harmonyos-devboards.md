# 鸿蒙开发板选型参考

## 全景概览

OpenHarmony 支持的开发板按能力分三档，从 LiteOS 轻量系统到完整分布式系统。

### 第一档：IoT 轻量（LiteOS-A/LiteOS-M, <128 MB RAM）

| 开发板 | 芯片 | CPU | RAM | NPU | 典型场景 |
|--------|------|-----|-----|-----|---------|
| Hi3861 | 海思 WiFi 模组 | MIPS 32-bit @ 120 MHz | 128 KB | 无 | 传感器节点、WiFi 控制 |
| ESP32-C3 鸿蒙版 | 乐鑫 ESP32-C3 | RISC-V 32-bit @ 160 MHz | 400 KB | 无 | WiFi IoT、智能家居 |

### 第二档：轻量系统（128 MB - 256 MB RAM）

| 开发板 | 芯片 | CPU | RAM | NPU | 摄像头 | 特色 |
|--------|------|-----|-----|-----|--------|------|
| T3 (Sipeed) | 瑞芯微 RV1103 | Cortex-M33 @ 200 MHz | 128 MB DDR | 2 TOPS | 双 MIPI CSI | AI 视觉、轻量 IoT |
| PV890 | 全志 PV890 | Cortex-A7 @ 1.5 GHz | 512 MB DDR | 2 TOPS | 双 MIPI CSI | 标准鸿蒙、HDMI 输出 |
| RK1126 | 瑞芯微 RK1126 | Cortex-A7 @ 1.2 GHz | 128 MB DDR | 1 TOPS | 单 MIPI CSI | 入门级标准系统 |

### 第三档：标准/高性能（256 MB+ RAM，完整分布式鸿蒙）

| 开发板 | 芯片 | CPU | RAM | NPU | 存储 | 接口 |
|--------|------|-----|-----|-----|------|------|
| RK3568 | 瑞芯微 RK3568 | 4×A55 @ 2.0 GHz | 4 GB DDR4 | 6 TOPS | eMMC 16 GB | USB 3.0, HDMI, PCIe |
| RK3588 | 瑞芯微 RK3588 | 4×A76+4×A55 @ 2.4 GHz | 8/16 GB | 6 TOPS | NVMe/eMMC 32 GB | 全接口 |
| Hi3516DV500 | 海思 | Cortex-A35 | 512 MB | 1 TOPS | - | 安防摄像头专用 |

## K230 对标分析

K230 核心参数：双核 RISC-V 64-bit @ 1.2 GHz, 2 TOPS VPU, 512 MB RAM, 双摄, H.264, ~1W

| 对比维度 | K230 | RV1103 T3 | PV890 | RK3568 |
|---------|------|-----------|-------|--------|
| AI 算力 | 2 TOPS | 2 TOPS | 2 TOPS | 6 TOPS |
| CPU 算力 | 双核 RISC-V 1.2G | M33 200M | A7 1.5G | A55×4 2.0G |
| 内存 | 512 MB | 128 MB | 512 MB | 4 GB |
| 摄像头 | 双 MIPI CSI | 双 MIPI CSI | 双 MIPI CSI | 双 MIPI CSI |
| 功耗 | ~1W | ~2W | ~3W | ~5W |
| 鸿蒙支持 | ❌ | ✅ 轻量 | ✅ 完整 | ✅ 完整 |
| 架构 | RISC-V 64 | ARM 32 | ARM 32/64 | ARM 64 |
| 工具链 | MicroPython | ArkTS+C/HDF | ArkTS+C/HDF | ArkTS+C/HDF |

## 关键结论

1. **K230 跑不了鸿蒙**：架构不兼容（64-bit RISC-V vs ARM）、外设驱动缺失（MIPI CSI、VPU、SPI OLED）、工具链不通（.kfpkg vs HAP）。
2. **RV1103 T3 是对等替代**：AI 算力和摄像头完全对等，但功耗更差、内存更小。核心价值是获得鸿蒙生态。
3. **PV890 是超越替代**：全维度对等或更强，运行鸿蒙完整版，唯一短板是功耗较高。
4. **RK3568 是未来-proof**：算力 10×、内存 8×，可以跑轻量级量化 LLM，是研究用最佳选择。

## 采购渠道

- **PV890**: 淘宝"PV890 开发板 鸿蒙"，价格 250-350 元
- **RK3568**: 淘宝"RK3568 开发板 鸿蒙" 或 Firefly 官网，价格 350-500 元
- **RV1103 T3**: 淘宝"RV1103 鸿蒙开发板"，价格 150-250 元
