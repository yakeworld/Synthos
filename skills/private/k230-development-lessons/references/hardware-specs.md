# K230 硬件规格参考

## SoC: Sipeed Kendryte K230

| 参数 | 规格 |
|------|------|
| **CPU** | 双核 RISC-V 64-bit @ 1.2 GHz (Sipeed 定制) |
| **NPU** | 2 TOPS INT8 / 1 TOPS FP16 @ 400 MHz |
| **内存** | 512 MB LPDDR4 |
| **存储** | 8 GB eMMC + SD 卡插槽 |
| **摄像头** | 双 MIPI CSI (gc2093) |
| **显示** | 1.14" SPI OLED (135×240) |
| **视频编码** | H.264 硬件编码器 |
| **功耗** | ~1W |
| **架构** | RISC-V 64-bit |
| **USB** | CDC ACM (串口) + PTP (gphoto2) |

## NPU 算力说明

**2 TOPS INT8 @ 400 MHz** 是 K230 的唯一正确规格。

常见混淆：
- **RV1126**: 6 TOPS NPU（瑞芯微，ARM Cortex-A7）
- **RK3568**: 6 TOPS NPU（瑞芯微，ARM Cortex-A55）
- **K230**: **2 TOPS** NPU（Sipeed 自研 RISC-V SoC）

K230 与 RK3568/RV1126 的 6 TOPS NPU **差三倍**。K230 是低功耗边缘 AI 摄像头定位，不是中端计算平台。

## 固件信息

| 参数 | 值 |
|------|------|
| **固件品牌** | Kendryte |
| **固件产品** | CanMV |
| **USB VID/PID** | 1209:abd1 |
| **串口路径** | /dev/openmvcam → /dev/ttyACM0 |
| **波特率** | 115200 |
| **GVFS PTP** | gphoto2://Kendryte_CanMV_001000000/ |
| **固件版本** | bcdDevice 2.00 (0x0100) |

## 诊断提示

- lsusb 成功 ≠ 串口可用。设备可能卡死但 USB 枚举仍成功。
- 串口无输出时，gvfs PTP 可能仍可枚举文件（PTP 走 USB bulk endpoint，不走串口）。
- dmesg 中 `device descriptor read/64, error -32` 表明 USB 通信层有硬件级错误。
