---


name: viewpoint-verification
description: "Directory index for viewpoint-verification: viewpoint-verification"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "hypothesis: str, context: dict -> verification_report: dict (score, evidence, counter_evidence, confidence)"
    atom_type: skill
    priority: P1
    related_skills: []
---





# Viewpoint Verification

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考
## IO_CONTRACT

- **input**: `hypothesis: str, context: dict` — 任务描述、参数配置
- **output**: `verification_report: dict (score, evidence, counter_evidence, confidence)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 验证清单 · VERIFICATION

1. **输入验证**: {输入条件是否完整}
2. **输出验证**: {输出格式是否符合预期}
3. **边界验证**: {边界条件是否处理}
4. **错误处理**: {异常场景是否覆盖}


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。

