# K230 4D-EyeTraker 完整技术规格

## 硬件平台

- **主控芯片**: Kendryte K230（RISC-V双核）
- **芯片级特性**: KPU神经网络处理器 + AI2D硬件加速器
- **固件**: CanMV (K230 SDK r273db2e) + MicroPython (029513) + RTSmart RTOS
- **构建时间**: 2026-01-20 01:05 CST
- **设备名称**: 4D-EyeTraker（OLED显示）

## 摄像头规格

| 分辨率 | FPS |
|:-------|:----|
| 1920×1080 | 30 / 60 |
| 1280×960 | 60 |
| 1280×720 | 90 |

- **接口**: MIPI CSI ×3（Camera 0左 / Camera 1右 / Camera 2前）
- **像素格式**: RGB565 / GRAYSCALE / YUV420SP
- **双摄同步**: 支持，双摄模式可同步拍照/录像

## 推理模式性能

| 参数 | 默认值 |
|:-----|:-------|
| 传感器输入 | 1280×720 @ 90fps |
| 模型输入 | 320×256（mbv2_encoder_reg） |
| 像素格式 | GRAYSCALE（推理最优） |
| AI预处理 | AI2D硬件加速（resize+pad） |
| 软件回退 | ulab.numpy |
| 输出保存 | 每100帧一批JSON |
| 实时推送 | WebSocket (192.168.1.3:8888) |
| 理论帧率 | 最高90fps（单摄） |

## 推理输出数据

```json
{
    "pupil": [x, y, w, h, angle],
    "iris": [x, y, a, b, angle],
    "iris_center": [x, y],
    "confidence": 0.0-1.0,
    "timing": {"preprocess": 5, "kpu": 10, "total": 15}
}
```

## AI模型清单

| 模型 | 输入 | 输出 | 用途 |
|:-----|:-----|:-----|:-----|
| eye_gaze.kmodel | 448×448 | pitch+yaw | 注视估计 |
| face_detection_320.kmodel | 320×320 | bbox+conf | 人脸检测 |
| face_landmark.kmodel | — | 关键点坐标 | 人脸关键点 |
| face_alignment.kmodel | — | 对齐矩阵 | 人脸对齐 |
| ocular_seg.kmodel | — | 眼部分割 | 眼部分割 |
| mbv2_encoder_reg.kmodel | 320×256 | 6通道参数 | 眼球运动回归（默认） |

路径: `/media/yakeworld/sda2/canmv/k230/examples/kmodel/`

## 软件架构

### 核心代码文件

| 文件 | 大小 | 功能 |
|:-----|:-----|:-----|
| inference.py | 核心 | 推理引擎（KPU+AI2D+后处理+推送+保存） |
| config.py | 5.6KB | 配置管理（JSON+序列号+模式getter） |
| hardware.py | 长 | 硬件抽象（OLED+按键+摄像头+WiFi） |
| state.py | 全局 | 全局状态与常量定义 |
| ai2d.py | 5.6KB | AI2D硬件加速预处理 |
| eye_gaze.py | 9KB | 人脸检测+注视估计完整demo |
| face_landmark.py | 6KB | 人脸关键点检测 |

### 配置参数 (config.json)

```json
{
    "wifi_ssid": "amazon",
    "wifi_password": "yakeworld",
    "inference_url": "http://192.168.1.100:8080/api/inference",
    "upload_url": "http://192.168.1.100:8080/api/upload",
    "inference_sensor_id": 1,
    "inference_width": 1280,
    "inference_height": 720,
    "inference_fps": 90,
    "inference_pixformat": "GRAYSCALE",
    "kmodel_path": "/sdcard/mbv2_encoder_reg.kmodel",
    "visualizer_enabled": false,
    "visualizer_ip": "192.168.1.3",
    "visualizer_port": 8888
}
```

## 存储结构

```
/data/
├── photos/001/         # 拍照会话
│   ├── cam0_000000.jpg
│   └── cam1_000000.jpg
├── videos/001/         # 录像会话
│   ├── video_cam0.mp4
│   └── video_cam1.mp4
└── inference/001/      # 推理会话
    ├── infer_batch_0000.json
    └── infer_batch_0001.json
```

## OLED显示

SSD1306 128×32，I2C（SCL=GPIO11, SDA=GPIO12）

**推理模式显示**:
```
INFER  TEMP:xx.xC    (模式+AI2D状态+温度)
FPS:xx.x ON OK       (帧率+可视化状态)
Sev:192.168.1.3      (服务器IP)
```

## GPIO引脚

| 引脚 | 功能 |
|:-----|:-----|
| GPIO11 | OLED SCL |
| GPIO12 | OLED SDA |
| GPIO18 | KEY0 拍照 |
| GPIO19 | KEY1 推理 |
| GPIO20 | KEY2 录像 |
| GPIO21 | KEY3 停止/复位 |
