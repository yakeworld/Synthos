# 3DeepVOG Paper — Key Reference for 3D Gaze Tracking

**Source**: PMC12880844 | *Digital Biomarkers* 2026;10(1):21

## Citation

Zhao J, Ahmadi SA, Decker J, Möhwald K, Zu Eulenburg P, Zwergal A, Flanagin VL, Wühr M. **3DeepVOG: An Open-Source Framework for Real-Time, Accurate 3D Gaze Tracking with Deep Learning.** *Digital Biomarkers*. 2026;10(1):21. DOI: 10.1159/000549948

**User's "ContraineF" → "3DeepVOG"**: The user's pronunciation/input "ContraineF" is a known misrecognition of this paper's name "3DeepVOG".

## Key Technical Contributions

### 1. Two-Sphere Anatomical Eyeball Model
- **Two-sphere anatomical eyeball model with corneal refraction correction**
- Geometrically interpretable estimation of 3D gaze (horizontal, vertical, torsional)
- **Directly applicable** to user's own 3D eyeball modeling research

### 2. Pupil + Iris Segmentation
- Automated pupil and iris segmentation via deep learning
- Combined with geometric estimation for full 3D pose

### 3. Torsion Tracking via Mini-Patch Template Matching
- Novel approach for real-time torsional eye tracking
- Not common in commercial systems

### 4. Performance
- **>300 fps** real-time operation
- **~0.1°** gaze error in all three dimensions
- Tested against clinical gold-standard VOG system in healthy controls
- Trained on **24,000+ annotated samples** across multiple devices and clinical scenarios

### 5. Clinical Validation
- Oculomotor measures (saccadic peak velocity, smooth pursuit gain, OKN slow-phase velocity) show good-to-excellent agreement with gold standard
- **Concept proof**: acute unilateral vestibular failure case — 3DeepVOG reliably captures 3D nystagmus

## Relevance to User's Research

This paper directly supports the user's eye-tracking BCI platform proposal:
- Two-sphere eyeball model → matches user's anatomical modeling approach
- Pupil/iris segmentation → core K230 AI model task
- Torsion tracking → novel capability not in most consumer systems
- ~0.1° accuracy → benchmark for user's K230 system (currently ~90Hz frame rate)
- Clinical validation framework → template for user's own BPPV/vestibular studies
- Open-source framework → can be adapted or compared against user's K230 pipeline

## Technical Comparison with K230

| Aspect | 3DeepVOG | K230 4D-EyeTraker |
|--------|----------|-------------------|
| Frame rate | >300 fps | 90 fps (1280×720) |
| Gaze error | ~0.1° | TBD (depends on calibration) |
| 3D model | Two-sphere anatomical | Geometric 3D reconstruction |
| Segmentation | DL-based pupil+iris | K230 .kmodel inference |
| Torsion | Mini-patch template matching | Not explicitly mentioned |
| Platform | Desktop/server GPU | K230 embedded SoC |
| Open source | Yes | Yes (CanMV firmware) |

## Full Abstract (English)

Eye movements are key biomarkers for diagnosing and monitoring neuro-otological, neuro-ophthalmological and neurodegenerative disorders. Video-oculography (VOG) systems enable detection of small, rapid eye movements and subtle oculomotor pathologies that may be missed during clinical exams. However, they rely on high-quality input, struggle with torsional movements, and are often limited by high costs in clinical and research settings.

To overcome these limitations, we developed 3DeepVOG, a deep learning-based framework for three-dimensional monocular gaze tracking (horizontal, vertical, and torsional rotation) that operates robustly across varied imaging conditions, including low-light and noisy environments. The method combines automated pupil and iris segmentation with geometrically interpretable estimation using a two-sphere anatomical eyeball model with corneal refraction correction. Torsion is tracked in real time using a novel mini-patch template matching approach. The system was trained on over 24,000 annotated samples obtained across multiple devices and clinical scenarios. Application was tested against a gold-standard VOG system in healthy controls. 3DeepVOG operates in real time (>300 fps) and achieves gaze errors of ~0.1° in all three dimensions. Oculomotor measures - saccadic peak velocity, smooth pursuit gain, and optokinetic nystagmus slow-phase velocity - show good-to-excellent agreement with a clinical gold-standard system. As proof of concept, we present a case of acute unilateral vestibular failure where 3DeepVOG reliably captures 3D nystagmus. 3DeepVOG enables accurate, quantitative eye movement tracking across three dimensions under diverse conditions. As an open-source framework, it provides an accessible and scalable tool for advancing research and clinical assessment in neurological oculomotor disorders.

## Full Abstract (Chinese Translation)

眼球运动是诊断和监测神经耳科、神经眼科和神经退行性疾病的**关键生物标志物**。视频眼震图（VOG）系统能够检测到临床检查中可能被忽略的小而快速的眼球运动和微弱的动眼病理。然而，现有系统依赖高质量输入、难以处理旋转运动，且在临床和研究环境中成本高昂。

为克服这些限制，我们开发了 **3DeepVOG**——一种基于深度学习的眼动追踪框架，实现了**三维单眼球追踪**（水平、垂直和旋转运动），可在低光和嘈杂等多种成像条件下鲁棒运行。该方法将**瞳孔和虹膜分割**与基于**两球解剖眼球模型**（含角膜折射校正）的几何可解释估计相结合。旋动通过新型**微型模板匹配**方法实时追踪。

系统使用了从多种设备和临床场景获得的超过**24,000个标注样本**进行训练。在健康对照中，与临床金标准VOG系统对比测试，3DeepVOG实时运行（**>300fps**），三维**眼动误差约0.1°**。动眼指标（扫视峰值速度、平滑追踪增益、光动性眼震慢相速度）与金标准系统显示出良好到优秀的一致性。

作为概念验证，我们展示了一个急性单侧前庭衰竭病例，3DeepVOG成功捕获了3D眼震。

3DeepVOG可在多样化条件下实现精确、定量的三维眼球运动追踪。作为开源框架，它为神经动眼疾病的研究和临床评估提供了可访问且可扩展的工具。
