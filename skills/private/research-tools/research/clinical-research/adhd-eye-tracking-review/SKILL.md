---



name: adhd-eye-tracking-review
description: "ADHD 眼动追踪综述：系统综述 ADHD 诊断中的眼动追踪技术与方法"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "topic: str, search_queries: list -> literature_review: dict (summary, key_findings, gaps, recommendations)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `topic: str, search_queries: list` — 用户请求描述、上下文信息
- **output**: `literature_review: dict — ADHD眼动综述`


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


> 对应原则：P2（机械原子暴露输入输出规范）

# Adhd Eye Tracking Review

ADHD眼动追踪生物标志物系统综述。



# Adhd Eye Tracking Review

