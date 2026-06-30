---



name: chinese-form-automation
description: 中文表格自动化：自动化处理中文表格/表单的录入、导出和数据校验
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "form_type: str, data: dict -> filled_form: dict (pdf, fields, completeness, errors)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Chinese Form Automation

自动填写中文政府/教育/学术申请表 — docx+xlsx模板填充。

详细内容请加载对应 references/ 目录下的参考文件。

## Environment Pitfalls

- **python-docx sandbox**: In Hermes sandbox (Python 3.12), `pip install python-docx` requires `--break-system-packages` flag (PEP 668). Python 3.11 environments do NOT need this flag. Always check Python version before pip install. If sandbox fails, use `terminal` tool directly.
- **markitdown docx**: Also requires `markitdown[docx]` extra for .docx conversion. Prefer direct `python-docx` library for reliability.

## User Preference Pitfalls

- User explicitly prefers **特色介绍** (highlight-based feature showcase) over **平台架构** (platform architecture). When asked to introduce Synthos or research capabilities, focus on distinctive/unique capabilities, not comprehensive platform overview. Do NOT create PPT unless explicitly requested — document (docx) is the default format.
- For file sending: Feishu requires specific chat_id format `feishu:oc_<id>` for direct messages, not bare `feishu`.
- NJJK (神经网络科技/脑机接口) 摸底模板：科技局标准调查表，按框架逐项填写。收到模板文件后直接按框架填充，不额外创建 PPT。

## References

- `templates/njjk-survey-template.md` — NJJK 摸底调查框架模板及 Synthos 填充指南
- `references/competition-application-workflow-2026-05-30.md`
- `references/competition-data-source-audit-2026-05-30.md`
- `references/hangzhou-medical-college-industry-mentor-2026.md`
- `references/researcher-profiling-via-notebooklm.md`

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



# Chinese Form Automation

