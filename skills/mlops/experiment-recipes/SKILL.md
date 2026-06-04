---
name: experiment-recipes
license: MIT
allowed-tools: Read
description: ML训练配方与预设——架构选择、训练循环、优化器、调度器、混合精度、内存优化、调试。 提炼自实战经验，非外部代码搬运。每个配方记录原理而非逐行代码。
metadata:
  synthos_atom_type: reference
  synthos_version: 1.1.0
  synthos_skill_md_hash: experiment-recipes-v1.1.0
  synthos_model_tested_on: '2026-05-15T00:00:00Z'
  synthos_data_access_level: raw
  synthos_author: Synthos
  synthos_absorbed_from: Synthos internal (ML training recipes from实战经验)
  synthos_absorbed_date: '2026-05-15'
  synthos_depends_on: knowledge-acquisition
  synthos:
    author: Synthos
    signature: 'input: dict -> output: dict'
    related_skills:
    - crispdm-helix-experiment
    - huggingface-hub
    - medical-image-centerline
    - remote-gpu-training
    - serving-llms-vllm
    version: 1.1.0
    tags:
    - training
    - recipes
    - ml
    - pytorch
    - reference
---


# Experiment Recipes / 实验配方参考

## 原理层·文言

> 实验之道，可复为先。配方精准，步骤清晰。
> 知其原理胜于录其代码，明其选择优于背其参数。
> 域有其模，模载其法。不搬外码，不存死例。

## 方法层·白话

**参考技能** — 为其他认知原子提供实验设计的原理性指导。
非代码仓库。Agent应理解原理后自行生成具体PyTorch代码。

---

## 触发条件

- 需要设计或设置深度学习训练实验
- 需要模型架构选择（按数据类型或数据规模）
- 需要训练循环模板（单GPU/DDP/FSDP）
- 需要优化器配置或学习率调度方案
- 需要混合精度训练或 torch.compile 加速
- 需要内存优化策略或 OOM 排障
- 需要 Karpathy 风格调试清单

---

## 1. 架构选择

### 按数据类型

| 数据类型 | 推荐架构 | 原理 |
|----------|---------|------|
| 图像（分类/检测） | ResNet / ViT | 层级特征提取 vs 全局自注意力 |
| 序列（文本/时序） | Transformer / LSTM | 长程依赖 vs 序列顺序敏感 |
| 图数据 | GCN / GAT | 邻居聚合 vs 注意力加权 |
| 多模态 | CLIP-style dual encoder | 独立编码+对比学习 |
| 表格数据 | MLP / TabTransformer | 简单有效 vs 特征交互建模 |

### 按数据规模

| 规模 | 策略 | 常见陷阱 |
|------|------|---------|
| <1K | 强正则化+小模型 | 过拟合 |
| 1K-10K | 预训练+微调 | 领域偏移 |
| 10K-100K | 全量训练+数据增强 | 欠拟合 |
| >100K | 大模型+分布式 | 通信开销 |

---

## 2. 训练循环模式

| 模式 | 适用场景 | 关键配置 |
|------|---------|---------|
| 单GPU | 原型验证、小模型 | DataLoader(num_workers>0) |
| DDP | 多GPU同机 | DistributedSampler, sync_bn |
| FSDP | 大模型显存不足 | sharding_strategy, cpu_offload |
| 函数式 | torch.compile / JIT | functional_call, grad accumulation |

---

## 3. 优化器与调度器

### 优化器选择

| 优化器 | 适合场景 | 学习率 | 关键参数 |
|--------|---------|:------:|---------|
| AdamW | 通用默认 | 3e-4 | weight_decay=0.01-0.1 |
| SGD+Momentum | CV大batch | 1e-1 (lr=0.1×batch/256) | momentum=0.9, nesterov |
| Adam | NLP/Transformer | 5e-5 | betas=(0.9,0.999) |
| Lion | 大模型训练 | 1e-4 | decoupled_weight_decay |

### 调度策略

| 策略 | 行为 | 适用 |
|------|------|------|
| Cosine | 余弦退火至0 | 通用，收敛稳定 |
| Linear Warmup+Decay | 先升后降 | Transformer类 |
| OneCycle | 升→降→微降 | 快速收敛 |
| ReduceLROnPlateau | 指标停滞时降 | 稳健训练 |

---

## 4. 混合精度与加速

| 模式 | 精度 | 加速比 | 注意 |
|------|:----:|:------:|------|
| FP32 | 32-bit | 1.0x | 基础 |
| AMP (fp16) | 混合 | 1.5-2x | loss scaling, 梯度裁剪 |
| AMP (bf16) | 混合 | 1.5-2x | 无需loss scaling |
| torch.compile | FP32/AMP | 1.2-2x | 首次编译慢，适合固定shape |

---

## 5. 内存优化（OOM排障顺序）

1. gradient checkpointing（时间换空间，省50%）
2. reduce batch size + grad accumulation
3. FSDP / DeepSpeed ZeRO
4. bf16 / fp16
5. `model.to(memory_format=torch.channels_last)`
6. `torch.backends.cuda.matmul.allow_tf32 = True`

---

## 6. Karpathy调试清单

1. 过拟合单batch → 确认loss可达0/近0
2. 可视化输入 → 确认数据加载正确
3. 梯度检查 → `grad.clamp_(-1.0, 1.0)` 看分布
4. 逐层激活统计 → 无NaN/Inf，均值方差合理
5. 验证集loss不下降 → 检查学习率/正则化
6. 训练loss不下降 → 检查梯度/初始化

---

## 验证清单

- [ ] 架构推荐基于数据类型+数据规模（非随意推荐）
- [ ] 训练循环模式匹配用户硬件环境（单GPU/DDP/FSDP）
- [ ] 混合精度配置与用户GPU型号兼容
- [ ] 调试清单覆盖至少Karpathy原始配方核心项
- [ ] 本技能不提供逐行代码——Agent应理解原理后自行生成
