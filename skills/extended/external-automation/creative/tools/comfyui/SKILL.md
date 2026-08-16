---
name: comfyui
description: comfyui
version: 1.0.0
category: creative
signature: 'comfyui -> creative: ComfyUI 节点式图像生成：通过 API 管理 ComfyUI 工作流，生成图像和视觉内容'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'prompt: str, model: str, parameters: dict -> image_results: list[Image]
      (url, dimensions, seed, model_version)'
    atom_type: skill
    priority: P1
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
## IO_CONTRACT

- **input**: `workflow_desc: str` — 用户请求描述、上下文信息
- **output**: `comfyui_workflow: dict — ComfyUI工作流`

> 对应原则：P2（机械原子暴露输入输出规范）

# Comfyui

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.

## 验证清单 · VERIFICATION

- [ ] 输入参数（`workflow_desc` 及相关 prompt/model/parameters）完整且有效，符合 IO 契约
- [ ] 生成的 ComfyUI 工作流为合法 dict 结构：节点连接、端口类型、参数键均符合 ComfyUI 规范，无悬空或未连线节点
- [ ] 工作流通过 ComfyUI API 实际执行成功，返回 `image_results`（含 url / dimensions / seed / model_version）且非空
- [ ] 返回图像可正常下载/打开，分辨率与 dimensions 字段一致
- [ ] 异常场景（空输入、超大参数、非法模型名）返回带上下文与恢复建议的错误信息，不暴露内部敏感状态

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[COMF-001]** 接收用户请求时 → 必须校验输入参数（workflow_desc）的完整性与有效性，确保符合 IO 契约
- **[COMF-002]** 执行核心操作前 → 需参考 scripts/ 或 references/ 目录下的详细文档，避免直接执行未验证的逻辑
- **[COMF-003]** 生成 ComfyUI 工作流时 → 输出必须严格遵循 dict 结构，确保节点连接与参数符合 ComfyUI 规范
- **[COMF-004]** 处理异常场景时 → 错误信息必须包含具体上下文及恢复建议，禁止暴露内部敏感状态
- **[COMF-005]** 验证输出结果时 → 需执行边界验证（空输入、极大值、异常场景），确保鲁棒性
- **[COMF-006]** 进行功能迭代或测试时 → 必须通过 Golden 集合（标准输入/预期输出/预期错误）验证，作为单一真理来源
