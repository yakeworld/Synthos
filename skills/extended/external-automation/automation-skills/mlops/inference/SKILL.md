---
name: inference
description: "Directory index for inference — mlops/inference   模型推理服务与优化"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: directory-index
    description: "Directory index for inference"
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []
    priority: P2

---
# mlops/inference — 模型推理服务与优化

## IO_CONTRACT

- **input**: `model_path: str, input_data: dict, parameters: dict` — 任务描述、参数配置
- **output**: `prediction: dict (output, confidence, metadata)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
| llama-cpp | llama.cpp local GGUF inference + HF Hub model discovery | quick |
| obliteratus | OBLITERATUS: abliterate LLM refusals (diff-in-means) | ultrabrain |
| outlines | Outlines: structured JSON/regex/Pydantic LLM generation | quick |
| vllm | vLLM: high-throughput LLM serving, OpenAI API, quantization | quick |

## 使用场景

- 本地推理：GGUF量化模型推理、vLLM高吞吐量服务
- 结构化输出：JSON Schema、正则表达式、Pydantic 模型生成
- 模型拒止消除：OBLITERATUS 去除 LLM 安全限制
- 模型发现：HF Hub 模型搜索和下载
