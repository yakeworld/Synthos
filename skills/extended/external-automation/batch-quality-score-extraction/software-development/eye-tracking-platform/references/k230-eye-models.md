# 眼球追踪模型清单 — .kmodel格式

## 模型存放位置

`/media/yakeworld/sda2/canmv/k230/examples/kmodel/`

## 人脸相关

| 模型 | 用途 | 输入 |
|:-----|:-----|:-----|
| face_detection_320.kmodel | 人脸检测（带anchors） | 320×320 |
| face_landmark.kmodel | 人脸关键点检测 | — |
| face_alignment.kmodel | 人脸对齐 | — |
| face_alignment_post.kmodel | 人脸对齐后处理 | — |
| face_liveness_rgb.kmodel | 人脸活体检测（RGB） | — |
| face_parse.kmodel | 人脸语义分割 | — |
| face_pose.kmodel | 人脸姿态估计 | — |
| face_recognition.kmodel | 人脸识别 | — |
| face_recognition_lite.kmodel | 轻量人脸识别 | — |
| face_recognition_mobile.kmodel | 移动端人脸识别 | — |
| face_registration.kmodel | 人脸注册 | — |
| face_registration_lite.kmodel | 轻量人脸注册 | — |
| yunet_640.kmodel | YUNet人脸检测 | 640×? |

## 眼动追踪

| 模型 | 用途 | 输入 |
|:-----|:-----|:-----|
| eye_gaze.kmodel | 人脸注视估计（pitch+yaw） | 448×448 |
| ocular_seg.kmodel | 眼部分割 | — |
| mbv2_encoder_reg.kmodel | **眼球运动编码/回归（默认）** | 320×256 |
| mbv2_encoder_regv1.kmodel | 眼球运动回归 v1 | 320×256 |

## 人体/手势

| 模型 | 用途 | 输入 |
|:-----|:-----|:-----|
| body_seg.kmodel | 人体分割 | — |
| hand_detection.kmodel | 手部检测 | — |
| hand_det.kmodel | 手部检测 | — |
| hand_reco.kmodel | 手部识别 | — |
| handkp_det.kmodel | 手部关键点检测 | — |
| gesture.kmodel | 手势识别 | — |
| person_detect_yolov5n.kmodel | 人体检测 YOLOv5n | — |
| person_keypoint_detect.kmodel | 人体关键点 | — |
| falldown_detect.kmodel | 跌倒检测 | — |
| nanotracker_head_calib_k230.kmodel | 头部跟踪校准 | — |
| nanotrack_backbone_sim.kmodel | 跟踪骨干网络 | — |

## 物体/分类

| 模型 | 用途 | 输入 |
|:-----|:-----|:-----|
| fruit_det_yolov5n_320.kmodel | 水果检测 YOLOv5n | 320×320 |
| fruit_det_yolov8n_320.kmodel | 水果检测 YOLOv8n | 320×320 |
| fruit_cls_yolov5n_224.kmodel | 水果分类 YOLOv5n | 224×224 |
| fruit_cls_yolov8n_224.kmodel | 水果分类 YOLOv8n | 224×224 |
| fruit_cls_yolo11n_224.kmodel | 水果分类 YOLO11n | 224×224 |
| fruit_seg_yolov5n_320.kmodel | 水果分割 YOLOv5n | 320×320 |
| fruit_seg_yolov8n_320.kmodel | 水果分割 YOLOv8n | 320×320 |
| fruit_seg_yolo11n_320.kmodel | 水果分割 YOLO11n | 320×320 |
| cropped_test127.kmodel | 测试模型 | 127×? |

## 其他

| 模型 | 用途 |
|:-----|:-----|
| hifigan.kmodel | HiFi-GAN语音合成 |
| zh_fastspeech_1_f32.kmodel | 中文FastSpeech 1 |
| zh_fastspeech_2.kmodel | 中文FastSpeech 2 |
| tts_zh.kmodel | 中文TTS |
| kws.kmodel | 关键词语音识别 |
| multi_kws.kmodel | 多关键词语音识别 |
| keyword_spotting.kmodel | 关键词 spotting |
| LPD_640.kmodel | 车牌检测 |
| yolo_license_plate_det.kmodel | 车牌检测YOLO |
| licence_reco.kmodel | 车牌识别 |
| ocr_det_int16.kmodel | OCR检测（int16量化） |
| ocr_rec_int16.kmodel | OCR识别（int16量化） |
| yolo11n-obb.kmodel | YOLO11n斜框检测 |
| yolov8n-obb.kmodel | YOLOv8n斜框检测 |
| yolov8n-pose.kmodel | YOLOv8n姿态估计 |
| yolov8n_224.kmodel | YOLOv8n标准检测 224 |
| yolov8n_320.kmodel | YOLOv8n标准检测 320 |
| yolov8n_seg_320.kmodel | YOLOv8n分割 320 |
| insect_det.kmodel | 昆虫检测 |
| landscape_multilabel.kmodel | 风景多标签分类 |
| veg_cls.kmodel | 植物分类 |

## K230模型格式说明

- **格式**: .kmodel，nncase编译器输出
- **运行时**: nncase_runtime库
- **执行引擎**: KPU（神经处理单元）+ AI2D（图像处理加速器）
- **量化**: 部分模型为int16量化（如OCR），部分为float32
- **模型输入**: 通过`kpu.load_kmodel()`加载，`kpu.set_input_tensor()`设置输入

## 模型加载模式

```python
import nncase_runtime as nn

kpu_session = nn.kpu()
kpu_session.load_kmodel("/sdcard/examples/kmodel/eye_gaze.kmodel")

input_tensor = nn.from_numpy(numpy_array)
kpu_session.set_input_tensor(0, input_tensor)
kpu_session.run()
output = kpu_session.get_output_tensor(0).to_numpy()
```
