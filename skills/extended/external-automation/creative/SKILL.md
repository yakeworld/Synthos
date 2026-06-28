---
name: creative
description: "直接调用子技能名称即可：`academic-diagram`、`manim-video`、`comfyui`、`p5js` 等。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---





## IO_CONTRACT

- **input**: `creative_request: str, style: str, output_format: str` — 创意请求、风格偏好、输出格式
- **output**: `creative_output: dict` — 创意产物（图表/视频/图像/代码）

> 对应原则：P2（机械原子暴露输入输出规范）


# Creative Tools

> 父级技能目录，包含 4 个子类别共 23 个技能。

## 子类别

- `diagrams/` — 图表与可视化（学术图、架构图、信息图、Excalidraw）
- `video-audio/` — 视频与音乐（Manim动画、FFmpeg、AI音乐、ASCII视频）
- `image-art/` — 图像与艺术（素描、像素艺术、漫画、信息图、Claude设计）
- `web-code/` — 网页与代码（p5.js创意编程、网页设计、TouchDesigner、Pretext）
- `tools/` — 创意工具（ComfyUI图像生成、论文转PPT、创意发散）

## 使用方式

直接调用子技能名称即可：`academic-diagram`、`manim-video`、`comfyui`、`p5js` 等。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


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
