---
name: automation-skills
description: automation-skills
version: 1.0.0
category: automation
signature: 'automation-skills -> automation: **触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md`
  中的 quality_score 并写入 `state'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


# Automation Skills

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

> (P032 语义去重: 移除 2 份截断的 Batch Quality Score Extraction 重复副本, 保留完整 1 份(含 Golden); 父技能标题归位顶部)

# Batch Quality Score Extraction

**触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。

## 背景

Synthos 管线中，每篇论文的 `01-manuscript/step_quality_check.md` 包含一个 JSON 块，其中 `score` 字段有多种格式。
批量处理时必须处理所有格式变体，且需要清理 LaTeX 反斜杠才能解析 JSON。

## 步骤

1. **列出目标论文目录** — 从 paper-queue.json 获取批次列表
2. **逐篇定位 `step_quality_check.md`** — 使用 `os.walk()` 查找，因为文件可能在不同子目录
3. **清理 LaTeX 反斜杠** — 在 `json.loads()` 之前移除所有非法 `\X` 转义
4. **提取分数** — 根据格式类型映射到 0-100 范围
5. **写入 state.json** — 更新 `quality_score` 字段，设置 `gate_status`

## 分数格式映射

| 格式 | 提取逻辑 | 示例 |
|