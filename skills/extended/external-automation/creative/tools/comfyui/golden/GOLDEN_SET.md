---
name: comfyui
description: comfyui 金测集 — ComfyUI 节点式图像生成（工作流 dict → API 执行 → image_results）的可执行测试
---

# 金测集: comfyui

> 来源: SKILL.md 验证清单 + Genes (COMF-001~006) + IO_CONTRACT + `workflows/` 标准工作流。
> 技能签名: `prompt, model, parameters -> image_results: list[Image] (url, dimensions, seed, model_version)`；
> IO_CONTRACT 入口为 `workflow_desc: str -> comfyui_workflow: dict`。
> 每个 case 验证工作流 dict 结构合法性（节点/端口/参数符合 ComfyUI 规范）、API 执行结果、
> 边界与异常处理（P1 可复现性、COMF-003/005）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：SDXL txt2img 工作流执行 | 工作流为合法 dict（节点连接/端口类型/参数键合规，无悬空节点）；API 执行成功返回非空 `image_results`（含 url/dimensions/seed/model_version）（COMF-001/003） |
| case_002 | 错误路径：非法模型名（ckpt 不存在） | 结构化错误含上下文（哪个节点/参数）+ 恢复建议（列出可用 ckpt / 修正 ckpt_name），不暴露内部敏感状态（COMF-004/005） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 工作流 dict 每个节点含 `class_type` + `inputs`；节点间连接为 `[node_id, port_index]` 形式且指向已定义节点（无悬空连接）；执行返回 `image_results` 非空且每项含 url / dimensions / seed / model_version 四字段
- case_002: 必须拒绝执行 —— 错误信息含"请求回声 + 触发条件（非法 ckpt_name + 所属节点）+ 恢复建议（列出可用模型 / 修正参数名）"，禁止仅返回通用错误（COMF-004）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命 |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 工作流执行结果 / 错误结构
- `verification`: 可执行的校验断言列表（dict 结构 / 连接合法性 / image_results 字段 / 错误上下文+恢复）

期望输出采用**语义等价判定**：
- 工作流 dict 必须无悬空节点与未连线端口（COMF-003）
- `image_results` 每项必须含 url / dimensions / seed / model_version 四字段
- 错误路径必须同时含 context 与 recovery 两个字段（COMF-004）
- 分辨率与 dimensions 字段一致（图像可下载/打开）

## 关联

- SKILL.md Genes: COMF-001~006
- SKILL.md 验证清单: 5 项（输入校验 / 工作流 dict 合法 / API 执行成功 image_results 非空 / 图像可打开且分辨率一致 / 异常含上下文+恢复）
- 标准工作流: `workflows/sdxl_txt2img.json`, `workflows/flux_dev_txt2img.json`, `workflows/sd15_txt2img.json` 等
- 脚本: `scripts/run_workflow.py`, `scripts/health_check.py`, `scripts/_common.py`
