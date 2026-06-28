---



name: comfyui
description: "Directory index for comfyui: comfyui"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "prompt: str, model: str, parameters: dict -> image_results: list[Image] (url, dimensions, seed, model_version)"
    atom_type: skill
    priority: P1
    related_skills: []
---




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

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
