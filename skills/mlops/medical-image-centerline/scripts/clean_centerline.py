#!/usr/bin/env python3
"""
clean_centerline.py — 从内耳二值标签提取三根半规管中心线

算法流程（5阶段）:
  Stage 1: 骨架化 + 图构建 → 前庭核心定位
  Stage 2: 图论最小环基 → 三半规管闭合回路
  Stage 3: 壶腹剔除（局部半径阈值）
  Stage 4: B样条平滑 → 可选曲率端点裁剪
  Stage 5: PCA法向量 + 管型命名（上/后/外）

输入:  二值标签 NIfTI (.nii.gz) 或 numpy 数组 (D, H, W)
输出:  3条中心线 + 元数据

依赖: numpy, scipy, scikit-image, networkx

完整代码路径:
  /media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/code/clean_centerline.py
"""
# This is a pointer file. The actual implementation is at the path above.
# Copy to local: cp /media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/code/clean_centerline.py .
