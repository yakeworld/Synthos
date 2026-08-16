---
name: powerpoint
description: powerpoint
version: 1.0.0
category: creative
signature: 'powerpoint -> creative: >-'
license: MIT
author: Synthos
metadata:
  synthos:
    version: 1.4.0
    author: Synthos
    signature: 'skill_set: pptx_files -> presentation: bytes'
    related_skills:
    - nature-paper2ppt
    - pil-image-generation
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

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# PowerPoint (.pptx) Generation

创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/模板。

详细内容请加载对应 references/ 目录下的参考文件。

## 环境陷阱

| 陷阱 | 修复 |
|: