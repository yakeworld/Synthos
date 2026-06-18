---
name: agent-orchestration-harness
description: Hermes（大脑）+ OpenCode（双手）双Agent工程化分工协议。 Hermes负责需求拆解/规范/架构检查，OpenCode负责代码生成/文件创建/验证。
version: 1.0.0
  >=80%置信度直接执行，不等人确认。
license: MIT
allowed-tools: shell skill_loader Read Write task_delegation file_search
metadata:
  synthos:
    author: Synthos
    signature: 'requirement: str -> spec_path: str, tasks_path: str, code_paths: list[str],
      review_passed: bool'
    related_skills:
    - debugging-hermes-tui-commands
    - embedded-python-modularization
    - github-agent-contributions
    - hermes-agent-skill-authoring
    - k230-canmv-debugging
    version: 1.0.0

---



# Agent Orchestration Harness — 双Agent工程化分工协议

## 原理层·文言

> 知者谋之，能者行之。
> Hermes为脑，OpenCode为手。脑不代手之劳，手不夺脑之谋。
> 规范在册，任务在表。文以载道，码以载器。
> 不信任报告，只信任读码。

## 方法层·白话

双Agent架构分工。Hermes作为规划中枢负责需求理解、规范生成、架构检查；OpenCode作为执行终端负责编码、建文件、验证。

核心三人文件：`spec.md`（规范）→ `tasks.md`（任务分拆）→ 审查报告。

## 触发条件

- 需要从零构建一个工程化项目
- 任务包含"写代码/建项目/做功能"等执行需求
- 需要架构规范先行、代码执行后的合规检查
- 多文件或多模块工程

## 工作目录

```
project/
├── harness/
│   ├── spec.md           ← 规范文档（Hermes生成）
│   ├── tasks.md          ← 任务拆解（Hermes生成）
│   ├── review.md         ← 架构审查报告（Hermes检查后生成）
│   └── tasks/            ← 子任务分拆（可选，复杂项目）
│       ├── T01-api-spec.md
│       └── T02-data-model.md
├── src/                  ← OpenCode生成的代码
└── tests/                ← OpenCode生成的测试
```

## 执行流程

### Phase 0：需求理解（Hermes）

1. 读取用户需求
2. 确定技术栈（语言/框架/数据库/第三方依赖）
3. 评估复杂度：简单（1-2文件）→ 单轮 | 复杂（3+文件/多模块）→ 双Agent

**复杂度判定矩阵：**

| 条件 | 判定 | 模式 |
|:-----|:-----|:-----|
| 单文件、<200行 | 简单 | 单Agent直写 |
| 2-3文件、有测试 | 中等 | Hermes拆任务→直写 |
| 3+文件、多模块、内部设计 | 复杂 | 双Agent Hermes+OpenCode |
| 已有代码需重构/扩展 | 复杂 | 双Agent |

### Phase 1：规范生成（Hermes）— 复杂项目才需此步

1. 读取项目现有代码结构（如有）
2. 生成 `harness/spec.md`：
   - 架构总览（层/模块/接口）
   - 关键设计决策（为什么选这个方案）
   - 数据流/控制流简图
   - 命名规范/目录结构约定
3. 生成 `harness/tasks.md`：
   - 每个任务一行：`T01 | 描述 | 依赖 | 验证条件`
   - 有依赖关系的排顺序，无依赖的标 `[PARALLEL]`
   - 每任务含验收标准（能跑什么命令验证）

### Phase 2：任务执行（OpenCode / delegate_task）

对每个任务：

```
Hermes: "你现在是java-developer/python-developer，
        请根据harness/tasks.md执行[TASK_ID]。
        输出到 src/ 目录。
        完成后运行验收命令并报告结果。"
```

**模式选择：**

| 场景 | 执行方式 |
|:-----|:----------|
| OpenCode可用 | delegate_task(acp_command="opencode") 或 terminal(pty=true) |
| 只有Hermes | delegate_task 派叶子节点，子Agent当Worker |
| 任务简单 | 直接terminal写代码 |

### Phase 3：架构合规检查（Hermes）

Hermes读取代码，不做信任假设：

1. `read_file` 读生成的每个文件
2. 检查：
   - [ ] 目录结构符合 spec.md
   - [ ] 命名规范一致
   - [ ] 接口签名匹配spec
   - [ ] 无硬编码密钥/路径
   - [ ] 异常处理完备
   - [ ] 注释/文档充分
3. 写审查报告到 `harness/review.md`

### Phase 4：修复循环

```
while review_passed == False:
    if 违规数 ≤ 3:
        Hermes直接 patch 修复
    else:
        Hermes: "现在还是java-developer，请根据 review.md 修复以下问题：[列表]"
        OpenCode修复
        Hermes重新审查（Phase 3）
    if 循环 > 3次:
        中断，报告当前状态给用户
```

## 已知陷阱

1. **OpenCode自报告=不可信** — 必须Hermes自己读代码验证
2. **上下文污染** — 每次切换Agent用独立指令，不传对话历史
3. **parallal任务冲突** — 两个Worker改同一文件 → 用 `[PARALLEL]` 标记确认无依赖
4. **spec过于详细** — spec写功能约束即可，不要写实现细节（那是OpenCode的职责）
5. **循环无上限** — 3次后必须中断，避免死循环
6. **OpenCode不自动知道项目标准** — 启动时设置 `workdir` 为项目根目录，OpenCode自动加载 `.opencode/rules.md`。不要在每条prompt中手动注入标准。

## 铁律：重复任务必走OpenCode

**Hermes 不执行机械性/重复性任务。** 以下场景一律 delegate 到 OpenCode：

| 场景 | 原因 | 做法 |
|:-----|:-----|:------|
| 批量文件生成 | 循环+写文件，纯机械 | 交给OpenCode写脚本执行 |
| 批量数据转换 | 格式转换/清洗 | 交给OpenCode |
| 多文件代码实现 | CRUD/样板代码 | 交给OpenCode（Hermes只审） |
| 测试用例编写 | 模式化工作 | 交给OpenCode |
| 重复性终端命令 | 同模式多次执行 | 交给OpenCode写脚本跑 |
| 代码格式化/lint修复 | 无智力含量 | 交给OpenCode |

**铁律：不自定OpenCode模型** — 让其用默认qwen3.6-35b。`--model`参数禁用。

## OpenCode 路径解析

安装方式不同，二进制路径不同：

| 安装方式 | 路径 |
|:---------|:-----|
| `npm i -g opencode-ai` | `~/.npm-global/bin/opencode` |
| `brew install` | 系统PATH内 |
| `curl -fsSL ...` | `~/.opencode/bin/opencode` |
| 通用 | `which opencode` 或 `which -a opencode` |

调用前用 `which opencode` 确认路径。PATH 找不到时 fallback 到 `~/.opencode/bin/opencode`。不硬编码路径到技能中。

**例外（Hermes自干）：**
- 1-2行的简单 patch
- `read_file` 读文件检查
- 架构决策/推理/规划

## 验证清单

- [ ] 需求复杂度已判定
- [ ] spec.md 已生成（含架构图/数据流）
- [ ] tasks.md 已生成（含依赖/验收标准）
- [ ] 每个任务执行后验收命令已跑
- [ ] Hermes已读代码做架构检查
- [ ] review.md 已生成
- [ ] 无违规 或 已在3轮内修复

## 命令层

- **Signature**: `requirement: str -> spec_path: str, tasks_path: str, code_paths: list[str], review_passed: bool`
- **Allowed tools**: shell, skill_loader, Read, Write, task_delegation, file_search
- **Output**: harness/ 目录 + src/ 代码 + review.md 审查报告
- **Fallback**: 无OpenCode时 → delegate_task叶子子Agent代替
