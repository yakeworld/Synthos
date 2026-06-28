---



name: researcher-portrait
description: "Directory index for researcher-portrait: researcher-portrait"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "researcher_name: str -> portrait: dict (publications, citations, networks, h_index, trajectory)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `researcher_name: str` — 用户请求描述、上下文信息
- **output**: `portrait: dict — 研究者画像`


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。


> 对应原则：P2（机械原子暴露输入输出规范）

# Researcher Portrait

中国研究者学术档案 — 论文/专利/项目结构化画像。
