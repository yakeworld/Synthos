---
synthos_atom_type: reference
name: experiment-recipes
version: 1.0.0
author: Synthos Agent
license: MIT
data_access_level: raw
allowed-tools: Read
dependencies: []
description: >
  ML training recipes & presets for deep learning experiments.
  Covers architect selection, training loops, optimizers, schedules,
  mixed precision, memory optimization, debugging, and experiment management.
tags: [training, recipes, ml, pytorch, reference]
bilingual: zh-en
---

# Experiment Recipes / 实验配方参考

> **A REFERENCE skill** — provides reusable recipes, presets, and code patterns
> that other cognitive atoms (e.g. `research-ideation`, `hypothesis-generation`)
> can load for technical guidance during experiment design and training setup.
>
> **这是一个参考技能** — 提供可复用的配方、预设和代码模式，
> 供其他认知原子（如 research-ideation、hypothesis-generation）在实验设计和训练配置时加载技术指导。

---

## 触发条件

在以下情况加载本技能：

- 用户需要设计或设置深度学习训练实验
- 用户需要选择模型架构（按数据类型或数据规模）
- 用户需要训练循环模板（单GPU/DDP/FSDP/函数式）
- 用户需要优化器配置或学习率调度方案
- 用户需要混合精度训练或 torch.compile 加速模式
- 用户需要内存优化策略或 OOM 排障
- 用户需要 Karpathy 风格调试清单
- 上游 cognitive 原子（如 research-ideation、hypothesis-generation）需要实验技术指导

---

## 验证清单

运行本技能后，确认以下检查项：

- [ ] 根据用户场景选择了正确的配方类别（架构/训练/优化/调度/精度/内存/调试）
- [ ] 推荐的架构决策基于数据类型+数据规模（非随意推荐）
- [ ] 提供的代码块可直接复制使用（含正确 import 和参数注释）
- [ ] 训练循环模式匹配用户硬件环境（单GPU/DDP/FSDP）
- [ ] 混合精度配置与用户 GPU 型号兼容
- [ ] 调试清单完整覆盖至少 Karpathy 原始配方项目

---

## [SYNTHOS_P0_ABSORBED_FROM]

- **Source**: NanoResearch / ml-training-recipes
- **Absorption Date**: 2026-05-14
- **Notes**: This reference skill distills practical deep learning training recipes
  from the NanoResearch ml-training-recipes corpus. All code blocks and patterns
  are preserved as-is from the original. Key contributions include: architect
  selection tables, training loop patterns, optimizer configs, LR schedules,
  memory optimization strategies, and the Karpathy debugging checklist.

---

## Table of Contents / 目录

1. [Overview / 概览](#1-overview--概览)
2. [Architect Selection Guide / 架构选择指南](#2-architect-selection-guide--架构选择指南)
3. [Training Loop Patterns / 训练循环模式](#3-training-loop-patterns--训练循环模式)
4. [Optimizer Configs / 优化器配置](#4-optimizer-configs--优化器配置)
5. [Learning Rate Scheduling / 学习率调度](#5-learning-rate-scheduling--学习率调度)
6. [Mixed Precision + Compilation / 混合精度与编译](#6-mixed-precision--compilation--混合精度与编译)
7. [Memory Optimization / 内存优化](#7-memory-optimization--内存优化)
8. [Debugging Checklist / 调试清单](#8-debugging-checklist--调试清单)
9. [Experiment Management / 实验管理](#9-experiment-management--实验管理)

---

## 1. Overview / 概览

This reference provides everything you need to design, implement, and debug
deep learning training experiments. Recipes are organized into the following
categories:

| Category | What You Get |
|----------|--------------|
| **Architect Selection** | Decision table by data type + data scale — pick the right model backbone |
| **Training Loops** | PyTorch training loop patterns (simple, DDP, FSDP, functional) |
| **Optimizers** | AdamW and Muon configurations with recommended hyperparameters |
| **LR Schedules** | Cosine decay and WSD (Warmup-Stable-Decay) implementations |
| **Mixed Precision** | `torch.amp` + `torch.compile` patterns for acceleration |
| **Memory Optimization** | Meta device, MFU calculation, OOM troubleshooting |
| **Debugging Checklist** | Karpathy's original recipe — find bugs fast |
| **Experiment Management** | TSV format for tracking runs and hyperparameters |

**Category's Chinese / 中文类别说明：**

| 类别 | 内容 |
|------|------|
| **架构选择** | 按数据类型 + 数据规模决策表，选对模型主干 |
| **训练循环** | PyTorch 训练循环模板（简单/DDP/FSDP/函数式） |
| **优化器** | AdamW 和 Muon 配置，推荐超参数 |
| **学习率调度** | Cosine 退火和 WSD（热身-稳定-退火）实现 |
| **混合精度** | `torch.amp` + `torch.compile` 加速模式 |
| **内存优化** | Meta device、MFU 计算、OOM 排障 |
| **调试清单** | Karpathy 原始配方 — 快速定位 bug |
| **实验管理** | TSV 格式追踪运行和超参数 |

---

## 2. Architect Selection Guide / 架构选择指南

### 2.1 By Data Type / 按数据类型

Select the model architecture based on your input data type:

| Data Type | Recommended Architectures | Why |
|-----------|--------------------------|-----|
| **Text** (LLM) | GPT / LLaMA / Mistral style Decoder-only Transformer | Autoregressive next-token prediction |
| **Text** (Encoder) | BERT / RoBERTa / ModernBERT | Bidirectional context, classification/embedding |
| **Image** (ViT) | ViT / SigLIP / DINOv2 | Patch-based vision transformer, scales with data |
| **Image** (CNN) | ConvNeXt / ResNet-RFB / EfficientNet | ClassicConv, good for smaller datasets |
| **Image** (DiT) | Diffusion Transformer (DiT) | Latent diffusion, SOTA generative modeling |
| **Video** | VideoMAE / TimeSformer / UniFormer | Spatiotemporal attention |
| **Audio** | Whisper / HuBERT / WavLM | Speech/audio representation learning |
| **Multi-modal** | LLaVA / Qwen2-VL / InternVL2 | Vision-Language, interleaved I/O |
| **Graph** | GCN / GAT / GraphGPS | Relational/structural data |
| **Tabular** | FT-Transformer / TabPFN / XGBoost | Structured table data (consider tree methods) |
| **Time Series** | PatchTST / TimesNet / Informer | Temporal pattern extraction |
| **3D / Point Cloud** | PointNet++ / PCT / Point Transformer | Sparse 3D coordinates |

### 2.2 By Data Scale / 按数据规模

| Data Scale | Model Size | Recommended Config |
|------------|-----------|-------------------|
| **<1K samples** | Tiny (1-10M params) | Use pretrained + LoRA/probing; avoid training from scratch |
| **1K-10K** | Small (10-100M) | Fine-tune pretrained; heavy augmentation |
| **10K-100K** | Medium (100M-1B) | Fine-tune or train from scratch with careful reg |
| **100K-1M** | Large (1B-7B) | FSDP / DeepSpeed, gradient checkpointing |
| **1M-10M** | XL (7B-70B) | 3D parallelism, activation offloading |
| **>10M** | XXL (70B+) | Megatron-LM, 4D parallelism, custom infra |

**Chinese / 中文说明：**

选择架构时的两条原则：

1. **数据类型优先**：先根据输入类型确定架构族（文本→Transformer、图像→ViT/CNN、表格→FT-Transformer……）
2. **数据规模调整**：根据可用样本量选择模型尺寸，样本越少越依赖预训练

---

## 3. Training Loop Patterns / 训练循环模式

### 3.1 Simple Training Loop (Single GPU)

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def train_one_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for batch_idx, (inputs, targets) in enumerate(dataloader):
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)

def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item()
    return total_loss / len(dataloader)
```

### 3.2 DDP Training Loop (Multi-GPU)

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def train_ddp(rank, world_size, model_fn, dataloader_fn, epochs):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)
    
    model = model_fn().to(rank)
    model = DDP(model, device_ids=[rank])
    dataloader = dataloader_fn(DistributedSampler)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        dataloader.sampler.set_epoch(epoch)
        model.train()
        for inputs, targets in dataloader:
            inputs, targets = inputs.to(rank), targets.to(rank)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
    
    dist.destroy_process_group()

# Launch: mp.spawn(train_ddp, args=(world_size, ...), nprocs=world_size)
```

### 3.3 FSDP Training Loop

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from torch.distributed.fsdp import ShardingStrategy

sharding_strategy = ShardingStrategy.SHARD_GRAD_OP  # hybrid shard
auto_wrap_policy = partial(
    transformer_auto_wrap_policy,
    transformer_layer_cls={TransformerBlock},  # your block class
)

model = FSDP(
    model,
    sharding_strategy=sharding_strategy,
    auto_wrap_policy=auto_wrap_policy,
    device_id=torch.cuda.current_device(),
    mixed_precision=None,  # handled separately via torch.amp
)
```

### 3.4 Functional Training Loop (for torch.compile / JIT)

```python
def train_step(model, inputs, targets, optimizer, criterion):
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
    return loss

# Compile the training step
compiled_train_step = torch.compile(train_step, mode="reduce-overhead")

for epoch in range(epochs):
    for inputs, targets in dataloader:
        loss = compiled_train_step(model, inputs, targets, optimizer, criterion)
```

---

## 4. Optimizer Configs / 优化器配置

### 4.1 AdamW (Standard)

```python
import torch

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=3e-4,          # peak learning rate
    betas=(0.9, 0.95), # default: (0.9, 0.999); 0.95 for stability in LLM
    eps=1e-8,         # numerical stability
    weight_decay=0.1, # typical: 0.01-0.1
)

# Recommended hyperparameters by model scale:
#  - <100M params:  lr=1e-3,  wd=0.01, betas=(0.9, 0.999)
#  - 100M-1B:       lr=5e-4,  wd=0.05, betas=(0.9, 0.95)
#  - 1B-10B:        lr=3e-4,  wd=0.1,  betas=(0.9, 0.95)
#  - >10B:          lr=1e-4,  wd=0.1,  betas=(0.9, 0.95)
```

### 4.2 Muon Optimizer

Muon is a second-order optimizer inspired by Newton-Schulz iterations. It's
designed for large-scale training and can outperform AdamW on LLM pretraining.

```python
import torch

@torch.no_grad()
def muon_update(p, lr, wd, momentum_buffer):
    """Simplified Muon update for a single parameter tensor."""
    if p.ndim < 2:
        return  # skip 1D params (biases, norms)
    
    # Orthogonalization via Newton-Schulz
    u, s, v = torch.svd(p.grad.float())
    ns_grad = (u @ v.T).to(p.dtype)
    
    # Apply momentum
    momentum_buffer.mul_(0.95).add_(ns_grad, alpha=1 - 0.95)
    
    # Weight decay
    p.mul_(1 - lr * wd)
    
    # Update
    p.add_(momentum_buffer, alpha=-lr)

class Muon(torch.optim.Optimizer):
    """
    Muon optimizer (simplified reference implementation).
    Paper: https://kellerjordan.github.io/posts/muon/
    """
    def __init__(self, params, lr=3e-4, wd=0.1, momentum=0.95):
        defaults = dict(lr=lr, wd=wd, momentum=momentum)
        super().__init__(params, defaults)
    
    @torch.no_grad()
    def step(self):
        for group in self.param_groups:
            lr = group['lr']
            wd = group['wd']
            momentum = group['momentum']
            
            for p in group['params']:
                if p.grad is None:
                    continue
                
                state = self.state[p]
                if 'momentum_buffer' not in state:
                    state['momentum_buffer'] = torch.zeros_like(p)
                
                muon_update(p, lr, wd, state['momentum_buffer'])
```

---

## 5. Learning Rate Scheduling / 学习率调度

### 5.1 Cosine Decay with Warmup

```python
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, SequentialLR

def get_cosine_schedule(optimizer, warmup_steps, total_steps, min_lr_ratio=0.1):
    """
    Cosine decay with linear warmup.
    
    Args:
        warmup_steps: number of linear warmup steps
        total_steps: total number of training steps
        min_lr_ratio: minimum LR as fraction of peak LR
    """
    warmup_scheduler = LinearLR(
        optimizer,
        start_factor=0.0,
        end_factor=1.0,
        total_iters=warmup_steps,
    )
    
    cosine_scheduler = CosineAnnealingLR(
        optimizer,
        T_max=total_steps - warmup_steps,
        eta_min=min_lr_ratio * optimizer.param_groups[0]['lr'],
    )
    
    return SequentialLR(
        optimizer,
        schedulers=[warmup_scheduler, cosine_scheduler],
        milestones=[warmup_steps],
    )

# Usage
# scheduler = get_cosine_schedule(optimizer, warmup_steps=1000, total_steps=50000)
```

### 5.2 WSD Schedule (Warmup-Stable-Decay)

WSD is a three-phase schedule: warmup → stable LR → rapid cosine decay to near-zero.

```python
import math

class WSDSchedule:
    """
    Warmup-Stable-Decay learning rate schedule.
    
    Phases:
        1. Warmup:    0 → peak_lr over warmup_steps
        2. Stable:    peak_lr for stable_steps
        3. Decay:     peak_lr → ~0 over decay_steps (cosine)
    """
    def __init__(self, peak_lr, warmup_steps, stable_steps, decay_steps):
        self.peak_lr = peak_lr
        self.warmup_steps = warmup_steps
        self.stable_steps = stable_steps
        self.decay_steps = decay_steps
        self.total_steps = warmup_steps + stable_steps + decay_steps
    
    def get_lr(self, step):
        if step < self.warmup_steps:
            # Phase 1: Linear warmup
            return self.peak_lr * (step / self.warmup_steps)
        
        elif step < self.warmup_steps + self.stable_steps:
            # Phase 2: Stable (constant peak LR)
            return self.peak_lr
        
        else:
            # Phase 3: Cosine decay to ~0
            decay_progress = (step - self.warmup_steps - self.stable_steps) / self.decay_steps
            decay_progress = min(decay_progress, 1.0)
            return self.peak_lr * 0.5 * (1.0 + math.cos(math.pi * decay_progress))
    
    def plot(self, steps=None):
        """Visualize the schedule (for Jupyter usage)."""
        steps = steps or self.total_steps
        import matplotlib.pyplot as plt
        lrs = [self.get_lr(s) for s in range(steps)]
        plt.plot(lrs)
        plt.xlabel("Step")
        plt.ylabel("Learning Rate")
        plt.title("WSD Schedule")
        plt.show()

# Usage
# schedule = WSDSchedule(
#     peak_lr=3e-4,
#     warmup_steps=2000,
#     stable_steps=50000,
#     decay_steps=10000,
# )
# for step in range(schedule.total_steps):
#     lr = schedule.get_lr(step)
#     for param_group in optimizer.param_groups:
#         param_group['lr'] = lr
```

---

## 6. Mixed Precision + Compilation / 混合精度与编译

### 6.1 Automatic Mixed Precision (AMP)

```python
import torch

def train_with_amp(model, dataloader, optimizer, criterion, device, scaler=None):
    model.train()
    scaler = scaler or torch.amp.GradScaler(device)
    
    for inputs, targets in dataloader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        
        with torch.amp.autocast(device_type=device.type):
            outputs = model(inputs)
            loss = criterion(outputs, targets)
        
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
```

### 6.2 torch.compile

```python
# Basic compilation
model = torch.compile(model, mode="reduce-overhead")

# Available modes:
# - "default":    balanced (trades off compile time for performance)
# - "reduce-overhead": best for small models / fast iter (favors speed)
# - "max-autotune":    slow compile, fastest runtime (use for prod)
# - "max-autotune-no-cudagraphs": autotune without CUDA graph constraints

# Full training with compile + amp
model = torch.compile(model, mode="reduce-overhead")
scaler = torch.amp.GradScaler()

for epoch in range(epochs):
    for inputs, targets in dataloader:
        optimizer.zero_grad()
        with torch.amp.autocast(device_type="cuda"):
            outputs = model(inputs)
            loss = criterion(outputs, targets)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

### 6.3 Recommended Precision Config by GPU

| GPU | Recommended Config |
|-----|-------------------|
| **A100 / H100** | `torch.float16` or `torch.bfloat16` + compile |
| **V100** | `torch.float16` AMP (no bf16 support) |
| **A6000 / 4090** | `torch.bfloat16` AMP + compile |
| **AMD MI250+** | `torch.bfloat16` AMP + compile |
| **Apple MPS** | `torch.float32` (AMP support limited) |

---

## 7. Memory Optimization / 内存优化

### 7.1 Meta Device Initialization

Initialize model parameters on meta device to avoid OOM when loading large models:

```python
import torch
from torch import nn

# Method 1: native meta device (requires PyTorch >= 2.0)
with torch.device("meta"):
    model = MyLargeModel(config)

# Method 2: using accelerate
from accelerate import init_empty_weights
with init_empty_weights():
    model = MyLargeModel(config)
```

### 7.2 MFU (Model Flop Utilization) Calculation

MFU measures how efficiently your GPU is being used during training:

```python
def estimate_mfu(model, batch_size, seq_len, step_time_ms, num_gpus=1):
    """
    Estimate Model Flop Utilization.
    
    Args:
        model: the model being trained
        batch_size: per-GPU batch size
        seq_len: sequence length
        step_time_ms: milliseconds per training step
        num_gpus: number of GPUs
    
    Returns:
        MFU as a float (0.0-1.0)
    """
    import torch.utils.flop_counter
    
    # Get model FLOPs per forward pass
    flop_counter = torch.utils.flop_counter.FlopCounter(model)
    dummy_input = torch.randint(0, 1000, (batch_size, seq_len))
    with flop_counter:
        model(dummy_input)
    flops_per_forward = flop_counter.get_total_flops()
    
    # Total FLOPs per step (forward + backward ≈ 2× forward)
    total_flops_per_step = flops_per_forward * 2 * num_gpus
    theoretical_flops = get_gpu_theoretical_flops() * num_gpus
    actual_flops = total_flops_per_step / (step_time_ms / 1000)
    
    return actual_flops / theoretical_flops
```

### 7.3 OOM Troubleshooting Checklist

Common causes and fixes:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| CUDA OOM at start | Batch too large | Reduce batch size; use gradient accumulation |
| OOM on long sequences | Attention O(n²) | Use Flash Attention; enable seq_len parallelism |
| OOM after N steps | Activation memory leak | Check for retained graph; use `.detach()` |
| OOM with FSDP | Sharding strategy wrong | Use `SHARD_GRAD_OP` instead of `FULL_SHARD` |
| OOM during compile | Compiler memory spike | Use `mode="reduce-overhead"` |
| Silent OOM | CPU-side memory leak | Clear cache: `torch.cuda.empty_cache()` |

---

## 8. Debugging Checklist / 调试清单

Karpathy's original debugging recipe, adapted for modern PyTorch:

1. [ ] **Overfit a single batch** — loss should go to near-zero
2. [ ] **Check loss function** — logits shape matches target shape?
3. [ ] **Check data pipeline** — visualize inputs, check for NaNs/infs
4. [ ] **Check gradient flow** — `grad` values should be non-zero everywhere
5. [ ] **Check learning rate** — too high diverges, too low stalls
6. [ ] **Check normalization** — BatchNorm layers in eval mode during inference?
7. [ ] **Check weight initialization** — default init OK for your activation?
8. [ ] **Check mixed precision** — no loss scale underflow?
9. [ ] **Check randomness** — set `torch.manual_seed` for reproducibility
10. [ ] **Simplify** — remove augmentations, halve model size, halve LR

**Chinese / 中文清单：**

1. [ ] **单批次过拟合** — loss 应降至接近零
2. [ ] **检查损失函数** — logits 形状与目标匹配？
3. [ ] **检查数据管道** — 可视化输入，检查 NaN/Inf
4. [ ] **检查梯度流** — 所有参数梯度非零
5. [ ] **检查学习率** — 过高发散，过低停滞
6. [ ] **检查归一化** — 推理时 BatchNorm 处于 eval 模式？
7. [ ] **检查权重初始化** — 默认初始化对激活函数是否合适？
8. [ ] **检查混合精度** — loss scale 没有下溢？
9. [ ] **检查随机性** — 设置 `torch.manual_seed` 确保可复现
10. [ ] **简化** — 去掉数据增强、模型减半、学习率减半

---

## 9. Experiment Management / 实验管理

Track experiments in a simple TSV format:

```tsv
experiment	model	dataset	lr	batch_size	epochs	best_val_loss	notes
exp001	LLaMA-160M	C4	3e-4	256	10	3.21	baseline
exp002	LLaMA-160M	C4	1e-4	512	10	3.15	lower lr, larger batch
exp003	LLaMA-160M	C4	3e-4	256	20	2.98	longer training
```

### Recommended Directory Structure

```
experiments/
├── exp001-baseline/
│   ├── config.yaml
│   ├── train.log
│   ├── checkpoint-latest.pt
│   ├── checkpoint-best.pt
│   ├── events.out.tfevents.*  (TensorBoard)
│   └── metrics.json
├── exp002-lower-lr/
│   └── ...
└── tracking.tsv
```

### Hydra / Config Management

For large-scale experiments, use Hydra for hierarchical config:

```yaml
# config.yaml
model:
  name: llama
  dim: 4096
  n_layers: 32
  n_heads: 32

training:
  lr: 3e-4
  batch_size: 256
  total_steps: 50000
  warmup_steps: 1000

data:
  path: /data/c4
  seq_len: 2048
```
