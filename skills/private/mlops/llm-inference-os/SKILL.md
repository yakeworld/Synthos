---
name: llm-inference-os
description: '**陷阱：Qwen3.5 是纯文本模型，Qwen3-VL 才是多模态。中间差一个字母（5 vs V），能力天壤之别。**'
signature: 'llm-inference-os -> mlops: synthetic skill for llm inference os'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**陷阱：Qwen3.5 是纯文本模型，Qwen3-VL 才是多模态。中间差一个字母（5 vs V），能力天壤之别。**'
    signature: 'llm-inference-os -> mlops: synthetic skill for llm inference os'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| 1 | Linux (Ubuntu/Debian) | ⭐⭐⭐⭐⭐ |
| 2 | Linux (RHEL/CentOS) | ⭐⭐⭐⭐ |
| 3 | Windows (WSL2) | ⭐⭐ |
| 4 | Windows (原生) | ⭐ |
| 5 | macOS | ⭐ |

## 引用研究

- **LLM-Pilot** (SC24, IBM/ETH): OS context switch/interrupt 对延迟有显著影响
- **Evaluating Containerization Overhead in MCP Servers** (AIxSE 2025): Linux container overhead 远小于 WSL2
- **Optimizing LLM Inference Clusters** (2025): Linux kernel tuning 对高并发吞吐影响 20-30%

## 陷阱 · 模型命名混淆

> **陷阱：Qwen3.5 是纯文本模型，Qwen3-VL 才是多模态。中间差一个字母（5 vs V），能力天壤之别。**
>
> 常见错误：用户说"用 Qwen3.5 跑图片"→ Qwen3.5 不支持图片
>
> **修复规则**:
> 1. 收到多模态需求时，首先确认模型名称是否含 "VL" 后缀
> 2. 如果用户说 Qwen3/3.5/3.6 而没有 VL/Coder 后缀 → 纯文本
> 3. 需要图片能力 → 推荐 Qwen2.5-VL 或 Qwen3-VL 系列
> 4. 参考完整型号辨析：`llm-model-selection` → `ref/qwen-model-variants.md`
>
> 文言：一字之差，天壤之别。先辨型号，再论部署。

## 关联

- `references/anonymous-networks-comparison.md` — 类 Tor 匿名网络项目对比
- `llm-model-selection` — Qwen 型号辨析、vLLM 多模态部署、显存估算

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 多模态需求：已确认模型名称含 "VL" 后缀；无后缀（Qwen3/3.5/3.6）判定为纯文本并拒绝图片任务（LLM-001）
- [ ] 需图片能力时已推荐 Qwen2.5-VL 或 Qwen3-VL 系列，而非 Qwen3.5（LLM-002）
- [ ] 部署平台按评级选择：优先 Linux (Ubuntu/Debian)，避免 Windows 原生与 macOS（LLM-003）
- [ ] 高并发推理集群已实施 Linux 内核调优并核实 20-30% 吞吐提升；OS 上下文切换/中断对延迟的影响已评估（LLM-004）
- [ ] 容器化/推理结论可追溯到引用研究（LLM-Pilot SC24、AIxSE 2025 容器开销、2025 集群优化），无编造数据（LLM-005）
- [ ] 推理/部署操作步骤可重复执行且结果可验证（LLM-006）
- [ ] 验证失败已记录原因与修复方案，以 Golden 集合（Input/Output/Error）为单一真理来源

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Llm Inference Os---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[LLM-001]** 收到多模态需求时 → 首先确认模型名称是否含 "VL" 后缀，若无则判定为纯文本模型并拒绝图片任务
- **[LLM-002]** 用户指定 Qwen3/3.5/3.6 等无后缀型号时 → 默认按纯文本能力处理，需图片能力时推荐 Qwen2.5-VL 或 Qwen3-VL 系列
- **[LLM-003]** 选择 LLM 推理操作系统时 → 优先选择 Linux (Ubuntu/Debian) 以获得最高性能评级，避免使用 Windows 原生或 macOS
- **[LLM-004]** 优化高并发推理集群时 → 实施 Linux 内核调优以获取 20-30% 的吞吐提升，并关注 OS 上下文切换对延迟的影响
- **[LLM-005]** 生成任何结论或数据时 → 必须经过事实核查且可追溯到具体证据源，严禁编造数据
- **[LLM-006]** 执行推理或部署操作时 → 确保每一步操作可重复且结果可验证，以维持系统的可复现性
- **[LLM-007]** 进行系统验证时 → 必须覆盖输入、过程、输出、边界及错误处理五个维度，且验证失败需记录原因和修复方案