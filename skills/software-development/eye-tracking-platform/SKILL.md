---
name: eye-tracking-platform
category: software-development
description: >-
version: 1.0.0
  三维眼动追踪平台 — K230嵌入式眼动仪硬件规格、AI推理管线、
  眼球追踪模型、数据采集与临床分析。覆盖：K230+CanMV固件、
  AI2D硬件加速预处理、KPU神经网络推理、眼动数据后处理、
  软硬件集成、VOR/kappa角/BCI应用。
allowed-tools:
- terminal
- read_file
- write_file
- search_files
triggers:
- eye tracking
- 眼动
- K230
- KPU
- AI2D
- eye_gaze
- 虹膜
- 瞳孔
- 4D-EyeTraker
- CanMV
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'eye_raw_frame -> gaze_params: dict'
    linked_subskills:
    - k230-canmv-debugging: K230板级调试（串口REPL、ampy传输、硬件编码器管线、传感器初始化顺序）
    - embedded-python-modularization: 嵌入式Python模块化（state.py模式、延迟导入、循环依赖消除）
    linked_references:
    - references/k230-eye-tracker-specs.md: K230 4D-EyeTraker完整技术规格 — 硬件平台、摄像头规格、推理性能、AI模型、软件架构、三种工作模式
    - references/k230-inference-pipeline.md: 推理管线详解 — AI2D预处理、KPU推理、后处理算法、置信度计算、数据输出格式
    - references/k230-eye-models.md: 眼球追踪模型清单 — eye_gaze.kmodel、face_detection.kmodel、ocular_seg.kmodel等
    - references/k230-embedded-architecture.md: 软件架构总览 — 采集层/预处理层/推理层三层管线、config.py/hardware.py/state.py模块职责

---


# Eye Tracking Platform — 三维眼动追踪系统

## 原理层·文言

> 双目红外，捕捉瞳孔虹膜之动。AI2D加速预处理，KPU推理后处理，
> 三维眼动数据如流，kappa角计算定位半规管，VOR增益量化前庭功能。

## K230 硬件平台

- **主控芯片**: Kendryte K230（RISC-V双核，带KPU神经网络处理器 + AI2D硬件加速器）
- **设备名称**: 4D-EyeTraker
- **固件来源**: CanMV（K230 SDK r273），基于MicroPython + RTSmart RTOS
- **摄像头接口**: MIPI CSI ×3（最多支持三摄）

### 摄像头规格

| 分辨率 | FPS |
|:-------|:----|
| 1920×1080 | 30 / 60 |
| 1280×960 | 60 |
| 1280×720 | 90 |

- **像素格式**: RGB565 / GRAYSCALE / YUV420SP
- **双摄同步**: Camera 0（左）+ Camera 1（右）

## 推理管线（三层架构）

```
采集层 → 预处理层 → 推理层
  ↓          ↓          ↓
Sensor    AI2D/SW     KPU
CSI       resize      .kmodel
          pad         后处理
          crop        JSON输出
```

### 1. 采集层
- Sensor → MIPI CSI → 帧缓冲（RGB565/GRAYSCALE/YUV420SP）
- 推理模式传感器输入: 1280×720 @ 90fps

### 2. 预处理层
- **AI2D硬件加速**: resize+pad/crop/affine（硬件实现，比软件快一个数量级）
- **软件回退**: ulab.numpy实现（AI2D失败时自动降级）
- 推理模式默认: GRAYSCALE格式

### 3. 推理层
- KPU加载.kmodel格式模型
- 输出: 瞳孔中心+宽高+角度、虹膜椭圆参数、置信度

## 推理输出数据格式

```json
{
    "pupil": [x, y, w, h, angle],      // 瞳孔中心+宽高+角度
    "iris": [x, y, a, b, angle],        // 虹膜椭圆参数
    "iris_center": [x, y],              // 虹膜中心
    "confidence": 0.0-1.0,              // 置信度(depth_sq≥0为1.0)
    "timing": {
        "preprocess": 5,               // AI2D预处理耗时(ms)
        "kpu": 10,                     // KPU推理耗时(ms)
        "total": 15                    // 总处理耗时(ms)
    }
}
```

**置信度算法**: 从模型输出提取眼球半径(r_eye)、瞳孔半径(r_iris)、瞳孔中心(ecx,ecy)、虹膜中心(icx,icy)，计算 depth_sq = r_eye² - r_iris² - (A²+B²)，其中 A=icx-ecx, B=icy-ecy。depth_sq<0 说明瞳孔投影超出眼球半径→置信度=0.0。

## AI模型（.kmodel格式）

| 模型 | 输入 | 用途 |
|:-----|:-----|:-----|
| eye_gaze.kmodel | 448×448 | 人脸注视估计（输出pitch+yaw） |
| face_detection_320.kmodel | 320×320 | 人脸检测 |
| face_landmark.kmodel | — | 人脸关键点检测 |
| face_alignment.kmodel | — | 人脸对齐 |
| ocular_seg.kmodel | — | 眼部分割 |
| mbv2_encoder_reg.kmodel | 320×256 | 眼球运动编码/回归（默认推理模型） |

## 三种工作模式

| 模式 | 按键 | 功能 |
|:-----|:-----|:-----|
| 拍照模式 | KEY0 (GPIO18) | 双摄同步拍照，JPG/BMP |
| 推理模式 | KEY1 (GPIO19) | AI模型实时推理→JSON+WebSocket推送 |
| 录像模式 | KEY2 (GPIO20) | H.265编码，MP4输出 |
| 停止复位 | KEY3 (GPIO21) | 停止当前模式并重启系统 |

## 网络与显示

- **WiFi**: STA模式，支持自动连接+IP获取
- **可视化推送**: WebSocket推送到服务器（默认 192.168.1.3:8888）
- **OLED**: SSD1306 128×32，I2C（GPIO11=SCL, GPIO12=SDA）
- **存储**: SD卡（/sdcard/）+ 内置Flash（/data/）

## 临床应用对接

- **Kappa角计算**: 视线方向与半规管平面夹角→受刺激半规管定位
- **VOR增益**: 前庭眼动反射功能定量评估
- **扫视动力学**: 幅度-速度关系、峰值速度、潜伏期
- **SIPP分析**: 平滑追踪中嵌入扫视的量化
- **BCI接口**: 眼动作为神经信号载体，绕过受损肢体通路

## 物理规格

| 项目 | 规格 |
|:-----|:-----|
| 主控 | Kendryte K230 |
| OLED | SSD1306 128×32 I2C |
| 摄像头 | MIPI CSI ×3 |
| 按键 | 4×GPIO (KEY0-KEY3) |
| 存储 | SD卡 + 内置Flash |
| 网络 | WiFi STA |
| 固件 | CanMV MicroPython + RTSmart |

## 代码文件结构

| 文件 | 功能 |
|:-----|:-----|
| `inference.py` | 推理引擎（KPU初始化+AI2D加速+后处理+推送+保存） |
| `config.py` | 配置管理（JSON加载保存+序列号+各模式getter） |
| `hardware.py` | 硬件抽象（OLED+4按键+摄像头初始化+WiFi） |
| `state.py` | 全局状态与常量 |
| `ai2d.py` | AI2D硬件加速预处理模块 |
| `eye_gaze.py` | 人脸检测+注视估计完整管线（demo） |
| `face_landmark.py` | 人脸关键点检测管线 |
| `config.json` | 运行时配置（WiFi、分辨率、模型路径、阈值） |

## Pitfalls

### AI2D与软件预处理选择
- AI2D硬件加速是默认路径，初始化失败自动降级为软件预处理
- 推理模式使用GRAYSCALE格式以最大化AI2D效率
- 预处理耗时在timing中记录，可用于性能监控

### 置信度边界条件
- depth_sq < 0 时置信度=0.0，C=0.0
- 这是瞳孔投影超出眼球半径的几何不一致信号
- 下游应用必须检查confidence字段，忽略低置信度帧

### 双摄同步丢帧
- 双摄像头同步录制时可能丢帧，导致实际FPS低于理论值
- 推荐单摄模式达到摄像头最大FPS@90
