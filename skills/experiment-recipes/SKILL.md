---
synthos_atom_type: reference
name: experiment-recipes
version: 1.0.0
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
# from accelerate import init_empty_weights
# with init_empty_weights():
#     model = MyLargeModel(config)

# Materialize on target device later
model.to_empty(device="cuda")
# or: model.to("cuda")
```

### 7.2 MFU (Model FLOPS Utilization) Measurement

```python
def compute_mfu(model, batch_size, seq_len, throughput, dtype_flops=2):
    """
    Compute Model FLOPS Utilization.
    
    Args:
        model: the model (needs to have config with hidden_size, num_layers, etc.)
        batch_size: tokens per batch (micro batch in FSDP)
        seq_len: sequence length
        throughput: tokens per second
        dtype_flops: factor (2 for fp16/bf16, 1 for fp32)
    
    Returns:
        mfu: fraction of theoretical peak FLOPS achieved
    """
    N = model.config.num_layers
    d = model.config.hidden_size
    V = model.config.vocab_size
    
    # Approximate FLOPs per token (Transformer decoder)
    flops_per_token = 6 * N * d * d + 12 * N * d * seq_len + 2 * N * d * V
    total_flops = flops_per_token * throughput
    
    # GPU theoretical peak (A100: 312 TFLOPS for fp16/bf16)
    gpu_peak_flops = 312e12  # adjust for your GPU
    mfu = total_flops / gpu_peak_flops
    
    return mfu

# Usage example
# mfu = compute_mfu(model, batch_size=8, seq_len=2048, throughput=50000)
# print(f"MFU: {mfu:.2%}")  # typically 40-55% is good
```

### 7.3 OOM Solutions Checklist

| Symptom | Solution |
|---------|----------|
| **CUDA OOM at model init** | Use meta device init → `to_empty()` |
| **CUDA OOM at forward pass** | Enable gradient checkpointing (`model.gradient_checkpointing_enable()`) |
| **CUDA OOM at backward pass** | Reduce batch size → micro-batching → gradient accumulation |
| **CUDA OOM with FSDP** | Reduce `limit_all_gathers`; use `SHARD_GRAD_OP` sharding |
| **CPU RAM OOM** | Use `torch.cuda.empty_cache()`; set `PYTORCH_NO_CUDA_MEMORY_CACHING=1` |
| **Activation memory spike** | Use activation offloading (DeepSpeed ZeRO-Offload) |
| **KV cache OOM (inference)** | Use PagedAttention / vLLM; reduce `max_seq_len` |
| **Slow but no OOM** | Not enough `torch.compile`; enable `channels_last` memory format |

**Quick OOM recovery (lossless):**
```bash
# Environment variable tweaks
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_DISTRIBUTED_DEBUG=INFO

# Or in Python:
# torch.cuda.set_per_process_memory_fraction(0.9)  # limit to 90% of GPU
```

---

## 8. Debugging Checklist / 调试清单

### 8.1 Karpathy's Recipe for Training (Preserved)

> This is the original Karpathy debugging checklist, reformulated for Synthos.
> Source: Andrej Karpathy's "A Recipe for Training Neural Networks" (karpathy/recipes).

```python
"""
KARPATHY'S DEBUGGING CHECKLIST
(用于训练神经网络的调试食谱)

OVERVIEW / 概述:
当你搭建完模型、开始训练却得不到合理结果时，用这个清单系统地排查问题。
依次执行，每步确认无误后再进到下一步。

1. 先别碰复杂架构
   - □ 先过拟合单批数据 (loss → 0) → 确认模型可以学习
   - □ 关闭所有正则化 (dropout=0, weight_decay=0, aug=off)
   - □ 用少量数据(1-5 batch)跑训练, loss应平滑下降
   - □ 若loss不降: 检查数据标签是否正确, 模型forward是否有梯度流

2. 数据预处理确认
   - □ 可视化输入数据: 确保喂入网络的数据是正确的
   - □ 检查标签分布: 确保没有标签错误/数据泄露
   - □ 确认数据增强不破坏标签语义

3. 模型初始化检查
   - □ 初始loss应与随机猜测一致 (分类: -ln(1/n_classes))
   - □ 初始logits不应全是0或NaN
   - □ 检查所有梯度存在 (没有None gradient)
   - □ 打印参数量: 确认模型没有"意外地小"

4. 训练循环正确性
   - □ model.train() / model.eval() 切换正确
   - □ optimizer.zero_grad() 在每个batch开始前调用
   - □ loss.backward() 后确认梯度不为0
   - □ 梯度裁剪: clip_grad_norm_ (max_norm=1.0) 防止爆炸

5. 学习率与优化器
   - □ 先用 lr=3e-4 (AdamW默认推荐)
   - □ 若loss震荡/发散: 降低lr × 0.3
   - □ 若loss停滞不降: 提高lr × 3.0
   - □ weight_decay不宜过大: 从wd=0.01开始

6. 数值稳定性
   - □ 检查loss中是否有NaN (detect early)
   - □ 使用AMP时检查scaler是否正常更新 (scaler.get_scale() > 0)
   - □ softmax + CE loss: 用内置nn.CrossEntropyLoss而非手动实现

7. Batch Size与梯度累积
   - □ 小batch size → 增大lr (linear scaling rule)
   - □ 梯度累积: total_batch = micro_batch × grad_accum_steps
   - □ 确认累积步骤中loss除以了grad_accum_steps

8. 验证/测试流程
   - □ 用与训练完全相同的预处理流程验证
   - □ 关闭gradient checkpointing在验证时
   - □ with torch.no_grad(): 确保不消耗显存

9. 性能基准
   - □ 计算tokens/s或samples/s并记录
   - □ 计算MFU (见7.2节) 确认GPU利用率
   - □ CPU预处理是否成为瓶颈? 用num_workers或NVIDIA DALI

10. 消融实验
    - □ 逐步添加组件: 先保证最简版本work
    - □ 每加一个组件后重新过拟合单批数据测试
    - □ 记录每次消融的loss曲线
"""
```

### 8.2 Quick Checks (Bash)

```bash
# Check GPU utilization
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader

# Check for NaN in model weights
python -c "
import torch
m = torch.load('model.pt', map_location='cpu')
for k, v in m.items():
    if torch.isnan(v).any() or torch.isinf(v).any():
        print(f'NaN/Inf found in: {k}')
"

# Monitor training in real-time
watch -n 1 nvidia-smi
```

---

## 9. Experiment Management / 实验管理

### 9.1 TSV Experiment Tracking Format

```tsv
# experiment-recipes master tracking sheet
# format: experiment_id<tab>date<tab>model<tab>dataset<tab>params<tab>lr<tab>schedule<tab>batch_size<tab>gpus<tab>val_loss<tab>best_epoch<tab>notes

exp-001	2026-05-14	GPT-125M	C4	tok=50257,d=768,l=12,h=12	3e-4	cosine	64	1	3.21	42	baseline
exp-002	2026-05-14	GPT-125M	C4	tok=50257,d=768,l=12,h=12	1e-3	cosine	64	1	3.15	38	lr=1e-3 sweep
exp-003	2026-05-15	GPT-350M	C4	tok=50257,d=1024,l=24,h=16	3e-4	wsd	128	4	2.89	55	wsd schedule test
exp-004	2026-05-16	GPT-1B	FineWeb	tok=50257,d=2048,l=32,h=32	3e-4	cosine	256	8	2.54	61	mixed precision=bf16
exp-005	2026-05-17	GPT-1B	FineWeb	tok=50257,d=2048,l=32,h=32	3e-4	cosine	256	8	2.48	63	+compile reduce-overhead
```

### 9.2 Python TSV Logger

```python
import csv
from datetime import datetime
from pathlib import Path

class ExperimentLogger:
    """Lightweight TSV experiment tracker."""
    
    def __init__(self, path="experiments.tsv"):
        self.path = Path(path)
        self.fields = [
            "experiment_id", "date", "model", "dataset", "params",
            "lr", "schedule", "batch_size", "gpus", "val_loss",
            "best_epoch", "notes"
        ]
        self._ensure_header()
    
    def _ensure_header(self):
        if not self.path.exists():
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(self.fields)
    
    def log(self, exp_id, **kwargs):
        row = {field: kwargs.get(field, "") for field in self.fields}
        row["experiment_id"] = exp_id
        row["date"] = str(datetime.now().date())
        
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields, delimiter="\t")
            writer.writerow(row)
    
    def load(self):
        """Load all experiments as list of dicts."""
        results = []
        with open(self.path, "r", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                results.append(row)
        return results
    
    def best(self, metric="val_loss", minimize=True):
        """Find best run by metric."""
        runs = self.load()
        if not runs:
            return None
        key = lambda r: float(r.get(metric, float("inf")))
        return min(runs, key=key) if minimize else max(runs, key=key)

# Usage
# logger = ExperimentLogger("experiments.tsv")
# logger.log("exp-001", model="GPT-125M", lr="3e-4", val_loss="3.21", ...)
# best = logger.best("val_loss")
```

### 9.3 Recommended Directory Structure

```
experiments/
├── exp-001_baseline/
│   ├── config.yaml          # full hyperparameter config
│   ├── logs/
│   │   ├── train.log
│   │   └── eval.log
│   ├── checkpoints/
│   │   ├── epoch_001.pt
│   │   ├── epoch_010.pt
│   │   └── best.pt
│   ├── tensorboard/         # or wandb run dir
│   ├── predictions/
│   │   └── test_outputs.npy
│   └── summary.json         # final metrics
├── exp-002_lr_sweep/
│   └── ...
└── experiments.tsv          # master tracking sheet
```

---

## Appendix / 附录

### A. Quick Reference Card / 快速参考卡

| Component | Recommended Default |
|-----------|-------------------|
| Optimizer | AdamW (lr=3e-4, betas=(0.9,0.95), wd=0.1) |
| Schedule | Cosine (warmup=5% of steps) or WSD |
| Precision | bf16 AMP (A100/H100), fp16 AMP (V100) |
| Compile | `torch.compile(mode="reduce-overhead")` |
| Batch Size | As large as GPU memory allows (power of 2) |
| Grad Clip | max_norm=1.0 |
| Weight Init | Default PyTorch (or init_weights from model zoo) |

### B. Common Errors / 常见错误

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `CUDA error: device-side assert` | Label out of range | Check `targets.max() < num_classes` |
| `RuntimeError: Expected all tensors to be on same device` | Mixed device tensors | Unified `to(device)` |
| `OutOfMemoryError` | GPU memory exhausted | See §7.3 |
| `NaN in loss` | Exploding gradients / bad LR | Reduce lr, add grad clip |
| `No improvement in val loss` | Overfitting / wrong schedule | Check reg, reduce capacity |

### C. Environment Setup / 环境配置

```bash
# Recommended PyTorch version
pip install torch>=2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For distributed training
pip install torchdistx fairscale

# For experiment tracking
pip install wandb tensorboard

# For data loading optimization
pip install nvidia-dali-cuda110
```
