---
name: evaluation
description: "Directory index for evaluation — mlops/evaluation   模型评估与实验追踪"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: directory-index
    description: "Directory index for evaluation"
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []
    priority: P2

---
# mlops/evaluation — 模型评估与实验追踪

## IO_CONTRACT

- **input**: `model_config: dict, benchmark_dataset: list` — 任务描述、参数配置
- **output**: `evaluation_results: dict (metrics, scores, comparison)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
| lm-evaluation-harness | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.) | quick |
| weights-and-biases | W&B: log ML experiments, sweeps, model registry, dashboards | quick |

## 使用场景

- 模型基准测试：MMLU、GSM8K、HellaSwag 等标准 benchmark
- 实验追踪：记录训练参数、指标、超参数搜索
- 模型注册：管理模型版本和部署流水线
