# mlops/inference — 模型推理服务与优化

## IO_CONTRACT

- **input**:  — 任务类型、参数配置
- **output**:  — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

> mlops 子技能目录，提供模型推理服务、量化、结构化输出和推理优化能力。

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
