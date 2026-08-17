---
name: chinese-form-automation
description: 中文表格/表单自动化的金测集：覆盖 NJJK 摸底模板填充（正常路径）与模板缺失/字段缺失校验（错误路径）
---

# 金测集: chinese-form-automation

> 本集合是本技能验证的单一真理来源。所有改进必须通过 golden 测试。
> 用例文件位于 `cases/`，预期结果位于 `expected/`，同名对应（`case_XXX.json` ↔ `expected/case_XXX.json`）。

## 被测行为（来自 SKILL.md Genes）

- **CHIN-001** 中文表格/表单任务 → 优先用 `python-docx` 直接操作，不依赖 `markitdown` 转换。
- **CHIN-002** Python 3.12 沙箱安装 `python-docx` → 必须带 `--break-system-packages`（PEP 668）。
- **CHIN-004** 收到 NJJK（神经网络科技/脑机接口）摸底模板 → 按科技局标准框架逐项填充，不额外创建 PPT。
- **CHIN-005** 飞书发送文件 → chat_id 必须为 `feishu:oc_<id>` 格式，禁止裸 `feishu`。
- **CHIN-006/007** 执行前严格校验输入；异常必须给出含上下文与恢复建议的错误信息。

## 测试用例

| ID | 文件 | 描述 | 关键检查 |
|----|------|------|---------|
| 1 | `cases/case_001.json` | NJJK 摸底模板逐项填充（正常路径） | `tool == "python-docx"`，`ppt_generated == false`，字段一一对应无串位，`completeness == 1.0`，飞书 chat_id 为 `feishu:oc_<id>` 格式 |
| 2 | `cases/case_002.json` | 模板文件缺失 + 必填字段缺失（错误路径） | 返回 `status == "error"`，错误信息含具体上下文（缺失路径/字段名）与恢复建议，不产出半成品文档 |

## 预期结果结构

- `expected/case_001.json`: 期望的 `filled_form`（pdf/docx 路径、fields 填充映射、completeness、errors 为空）+ 逐项检查。
- `expected/case_002.json`: 期望的错误结构（status、error.context、error.recovery、产出物为空）。

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 每个 case 的 JSON 均可被 `python3 -c "import json,sys; json.load(open(sys.argv[1]))"` 解析

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |
