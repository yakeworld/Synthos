---

name: competition-submission
related_skills: ["argument-expression"]
description: End-to-end preparation of AI/tech/innovation competition submissions. Extract requirements, map to scoring criteria, generate documents, produce submission checklist. Covers medical AI, tech innovation, academic conferences, Chinese government grants.
version: 1.0.0
allowed-tools:
- terminal
- file
- web
- search
license: MIT
author: Synthos
metadata:
  synthos:
    version: 2.0.0
    author: Synthos
    signature: 'competition_doc: str -> submission_package: dict'


---
version: 1.0.0


## IO_CONTRACT

- **input**: `topic: str, requirements: dict` — 用户请求描述、上下文信息
- **output**: `submission: dict — 竞赛方案`


> 对应原则：P2（机械原子暴露输入输出规范）

# Competition Submission Pipeline

## 核心流程

```
输入(通知PDF/链接)
  ↓
Step 1: 需求提取 → 评分标准/格式要求/截止时间
Step 2: 能力映射 → 项目能力→评分标准矩阵
Step 3: 文档生成 → 技术规格/路线图/视频脚本/申报表
Step 4: 材料整合 → 提交包(zip/PDF)
Step 5: 质量审核 → 完整性/一致性检查
```

## Step 1b: 政府座谈会/政策对齐策略（新增）

适用于：政府产业规划座谈会、政策方案讨论会、专项资金申报前的策略准备。

**核心目标：** 将用户的技术/临床资产与政策方案中的"任务板块"一一映射，找到"嵌入点"，确定发言策略。

**流程：**
1. 读取政策方案全文，提取"主要任务"章节的每个子项（如：高校引领、产业孵化、临床资源、平台建设、材料研发）
2. 读取用户技术资产（论文、专利、设备、平台、团队、Synthos等科研方法论）
3. 逐条映射：政策任务 → 用户匹配度（⭐1-5）→ 可承担的具体板块 → 发言要点
4. 识别"空白机会"：政策中提到但用户尚未覆盖的方向，可作为未来申报切入点
5. 识别"已有闭环"：用户已完成临床转化的方向，强调"可复制性"
6. 输出：① 竞争力分析表 ② 建议承担板块 ③ 讨论会提问清单 ④ 3-5分钟发言草稿

**关键原则：**
- 政府方案中"主导/牵头"单位通常不是技术方，技术方应争取"核心成员"或"联合牵头"
- 强调"已有闭环"（临床痛点→机理→原型→验证）比"未来规划"更有说服力
- 将已有硬件/算法/论文打包为"技术壁垒"，而非单一论文
- 人才需求与政策中的"引育"章节挂钩

- `references/policy-alignment-workflow.md` — 政府座谈会准备模式
- `references/data-elements-competition-cn.md` — 数据要素×大赛 申报指南（赛道选择+DOCX操作+Synthos定位）

## Step 1: 需求提取

从PDF或网页提取竞赛要求：

```bash
# PDF提取
curl -sL "https://..." | python3 -c "
import sys, pdfplumber
with pdfplumber.open(sys.stdin.buffer) as pdf:
    for page in pdf.pages: print(page.extract_text())
"

# 网页提取
curl -sL "https://..." | python3 -c "
import sys, re
html = sys.stdin.read()
# 提取表格/列表等结构化评分标准
"
```

输出结构化清单：`requirements/competition-reqs.json`

## Step 2: 能力映射

| 评分维度 | 权重 | 项目匹配能力 | 证据材料 |
|:---------|:----:|:------------|:---------|
| 创新性 | 30% | Synthos声明式架构 | 论文/架构图 |
| 技术深度 | 25% | 自进化引擎 | evolution日志 |
| 社会价值 | 20% | 医学AI应用 | 论文产出清单 |
| 可行性 | 15% | 已有完整管线 | paper-pipeline |
| 团队实力 | 10% | 论文+专利产出 | CV/成果列表 |

## Step 3: 文档生成

| 文档类型 | 模板 | 工具 |
|:---------|:-----|:-----|
| 技术规格书 | `references/tech-spec-template.md` | Markdown |
| 路线图 | `references/roadmap-template.md` | Mermaid timeline |
| 视频脚本 | `references/video-script-template.md` | 分镜脚本格式 |
| 申报表 | `references/form-filling-guide.md` | python-docx/pdf |
| PPT | `references/presentation-template.md` | python-pptx |

详见各模板文件。

## Step 4-5: 整合与审核

```bash
# 打包
zip -r submission.zip submission/ -x "*/.*"

# 完整性检查
# 检查是否涵盖所有评分维度/格式要求/截止时间
```

## 参考文件

- `references/tech-spec-template.md` — 技术规格书模板
- `references/roadmap-template.md` — 路线图模板
- `references/video-script-template.md` — 视频脚本模板
- `references/form-filling-guide.md` — 中国申报表填写指南
- `references/presentation-template.md` — 答辩PPT模板
- `references/symposium-prep-patterns.md` — 政府座谈会准备模式

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

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
