# 多任务模型消融试验设计 — Eye-Tracking Pipeline

## 场景

多任务深度学习模型（分割 + 参数回归 + 时序建模）的系统性消融设计。
源自 `/mnt/nfs` 下的 T3EM 训练管线 (`train_ablation.py`)。

## 核心架构模式

```
输入: 视频序列 (B, T, C, H, W)
       ↓
  编码器 (MobileNetV2 / ViT / ResNet)
       ↓
  ┌─────────────────────────────────┐
  │           共享特征层              │
  └─────────────────────────────────┘
       ↓              ↓              ↓
  分割头           参数头          时序头
  (CE Dice)       (L1/SmoothL1)   (LSTM/GRU/Transformer)
       ↓              ↓              ↓
  背景/虹膜/瞳孔   静态4+动态4参数   扭转角/运动学
```

## 损失组件池（8项）

| 符号 | 名称 | 类型 | 作用 |
|------|------|------|------|
| `stat` | 静态参数回归 | L1/SmoothL1 | 眼球中心(x,y) + 半径 |
| `dyn` | 动态参数回归 | L1/SmoothL1 | 瞳孔中心 + 半径 + 角度 |
| `seg` | 分割交叉熵 | CE | 背景/虹膜/像素级分类 |
| `dice` | 几何Dice损失 | Dice | 分割边界约束 |
| `lcom` | 中心线中心监督 | 距离场 | 分割中心 vs 参数中心对齐 |
| `param_seg_dice` | 参数引导分割Dice | 几何Dice | 参数→椭圆mask与分割一致性 |
| `edge` | 边缘梯度损失 | Sobel+L1 | 分割边界梯度 vs 真实边缘 |
| `tex` | 纹理一致性 | 结构相似/梯度 | 分割区域纹理一致性 |

## 消融阶段设计（27组实验模板）

### Phase A: 逐项增益 (exp1–exp7)
**目标**: 确认每个损失项的独立贡献

```
exp1: stat + dyn only (baseline)
exp2: + seg(CE)
exp3: + dice
exp4: + lcom
exp5: + param_seg_dice
exp6: + tex
exp7: + edge
```

**模式**: 每一项在前一项基础上增加一个新组件，保持其他为零。
**判定**: 如果某项增益 < 0.005 Dice，该项可能冗余。

### Phase B: 半监督弱监督 (exp8–exp20)
**目标**: 探索参数标注成本削减

```
关键设计:
- 本地数据: 仅用图像+分割掩码，丢弃参数标签 (自监督)
- OpenEDS: 保留完整标签 (全监督)
- 混合比例: local_ratio=0.5, openseds_ratio=0.5
- 自监督损失: edge + param_seg_dice + temporal (无需GT参数)
```

**弱监督权重扫描**: 对 edge, tex, lcom 进行网格搜索
```
edge: [0.05, 0.1, 0.3, 0.5, 1.0, 3.0, 5.0]
tex: [0.0, 0.1, 0.3, 1.0]
lcom: [0.0, 0.1, 0.3]
```

### Phase C: 冷启动→弱监督切换 (exp21–exp24)
**目标**: 探索训练策略对标注依赖的解耦

```
exp22: cold(50ep, full) → weak(50ep)
exp23: cold_full(50ep) → weak(50ep, different weights)
exp24: cold_full(10ep) → weak(60ep)
```

**策略**: 先用全监督快速收敛，后切换弱监督减少标注依赖。
**关键参数**: cold_epochs, weak_after_epochs, transition_to_weak

### 对照组 (exp25–27)
```
exp25: full GT supervision (reference, 80ep)
exp26: minimal GT: stat+dyn+seg only (reference)
exp27: exp2 pretrained + edge=0.05 (极弱边缘)
```

## 评估协议

### 核心指标
- `best_mean_dice = (val_dice_pupil + val_dice_iris) / 2`
- `final_train_loss`, `final_val_loss`
- 各分量损失追踪: `Stat`, `Dyn`, `CE`, `Dice`

### 早停
- `EarlyStopping(patience=10)`: 连续10轮无提升即停
- 每轮保存 checkpoint: `t3em_checkpoint_{ablation}.pth`
- 最优模型单独保存: `t3em_best_{ablation}.pth`

### 可视化
- 最优 epoch 输出: `save_prediction_visualization()`
- 输出目录: `visualizations/{ablation}/`
- 内容: 分割掩码 + 椭圆参数叠加 + 参数趋势图

## 训练配置模板

```python
config = {
    "epochs": 100,
    "batch_size": 8,
    "lr": 1e-4,
    "weight_decay": 1e-2,
    "scheduler": "ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-6)",
    "optimizer": "AdamW",
    "grad_clip": True,
    "seed": 42,
    "seq_len": 16,
    "num_workers": 4,
    "amp": True,  # GradScaler
}
```

## 数据混合协议

```python
# 半监督模式: OpenEDS全监督 + 本地自监督
train_ds = ConcatDataset([
    Eye_openeds_Dataset(csv, root, use_labels=True),   # 全监督
    Eye_HD_Dataset(csv, root, use_labels=False),        # 自监督 (丢弃参数)
])
```

**自监督模式**: `Eye_HD_Dataset` 的 `use_labels=False` 时，仅计算
`edge + param_seg_dice + temporal` 损失，不使用 GT 参数值。

## 权重恢复与预训练

```bash
# 从exp2继续训练 (预训练权重初始化)
python train_ablation.py --ablation exp27 --resume_from exp2

# 手动恢复检查点 (覆盖预训练权重)
# load_checkpoint() 在 resume_weights_path 之后加载
# 如果 checkpoint 不存在，静默从 epoch 1 开始
```

**关键**: 预训练权重加载后，`load_checkpoint()` 会覆盖。如果 checkpoint
文件不存在，`load_checkpoint` 静默跳过，不影响预训练初始化。

## 输出文件约定

```
checkpoints/
├── t3em_best_{ablation}.pth       # 最优模型权重
├── t3em_checkpoint_{ablation}.pth # 每轮检查点
└── t3em_best_{ablation}_metrics.json  # 最终指标 (JSON)

logs/
└── training_{ablation}.log         # 训练日志

visualizations/
└── {ablation}/                     # 最优预测可视化
```
