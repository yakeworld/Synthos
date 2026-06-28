---
name: competition-application
description: 中国行业/政府大赛申报书撰写 — 数据要素×大赛、数智教育大赛等。覆盖项目定位、Synthos能力包装、DOCX模板填充、PPT路演制作、材料清单管理。
version: 1.0.0
author: Synthos
license: MIT
tags: [competition, application, government, bidding, docx]
signature: "competition-application -> processed_result"
---

# Competition Application Writing（大赛申报书撰写）

## 工作原理 · 文言

> 三叠叙事：痛→方→效。
> 不立空名，以数据为骨，以成果为肉。
> 旧材新用，实时更新，不凭印象填数字。

## 触发条件

- 用户要求撰写或修改**大赛/政府项目申报书**
- 涉及 **Synthos 作为申报主体**的竞赛材料
- 需要填写 **DOCX 表格模板 + 长篇文字段落**
- 需要制作**路演PPT**

## 工作流程

### Step 0：预检（必做）

> **反模拟检测**：非任务开始前检测，而是执行中按技能步骤操作。
> 先查再写，不臆测。

1. **查历史申报**：先搜索 `Synthos-competition` 目录或 session 历史，确认是否有之前申报过的相同或类似项目
   ```bash
   ls /media/yakeworld/sda2/Synthos-competition/
   ```
2. **查 Synthos 最新状态**：从 evolution-state.json 提取实时数据
   ```python
   # 关键字段
   version, cycle, overall_score, status
   skills_count = $(find skills -name "SKILL.md" | wc -l)
   papers_pipeline = state.paper_submission.papers
   ```
3. **查申报书模板结构**：用 python-docx 读表格行数、段落索引，定位每个字段位置

### Step 1：定位赛道

申报书表格中 **赛道（赛道及参赛方向）** 是单选。根据用户背景选：

| 适合赛道 | 匹配条件 | 避坑 |
|:--------|:--------|:----|
| 医疗健康 | 医院/临床/科研实验室 | 公立医院不要选"数据基础设施"——需填营收/融资/Token消耗 |
| 科技创新 | 高校/科研院所 | 同上有财务数据问题 |
| 数据基础设施 | 企业/数据交易平台 | **医院实验室不选此赛道** |

确认赛道后，在申报书表格中标记"√已选：XXX"。

### Step 2：三层叙事结构（通用模板）

```
第1层：痛点（Pains）
  描述行业数据治理的三大危机：质量危机、可复现危机、选择困难
  引用具体数据（70% AI论文有数据泄露、PIDD近50% Insulin=0等）

第2层：方案（Solution）
  描述 Synthos 自主进化AI智能体架构
  CRISP-DM Helix 可审计方法论 + G1-G7质量门控
  核心技术栈：209个SKILL.md技能模块、AKNE知识图谱、30模型基准

第3层：成效（Results）
  量化指标：175轮进化、0.9647评分、5篇管线论文
  已发表成果：6篇BPPV论文（Frontiers in Neurology等）、Kaggle推荐
  团队能力：博士后4名、发明专利20+项
```

### Step 3：DOCX模板填充

```python
from docx import Document
doc = Document('template.docx')
table = doc.tables[0]

# 表格字段定位方法：
# - 读行数：len(table.rows)
# - 读列数：len(table.rows[ri].cells)
# - 合并单元格问题：set_cell 后内容会传播到同行的合并单元格

# 建议长文本写入策略（避免Python编码问题）：
# 1. 将文本写入 JSON 文件
# 2. Python脚本读取 JSON 再填充到对应段落索引
```

**常见陷阱：**
- **合并单元格**（merged cells）：DOCX模板的表格使用大量合并单元格。set_cell写入某个字段后，同行的其他合并单元格自动收到相同内容。解决方案：只写入一个非合并的单元格，或写入后清空传播内容。
- **段落索引定位**：申报书的长文本段落（项目背景、解决方案等）紧跟在标题段落之后。用 `doc.paragraphs[idx]` 定位时，先打印所有段落确认索引。
- **清除模板说明文字**：模板中有大量"（介绍参赛项目的背景...）"等说明文字，填入真实内容后应清除。

### Step 4：PPT制作（可选）

模板在 Synthos-competition 目录，可参考之前 PPT 的10页结构：
1. 封面（项目名+团队）
2. 项目概述
3. 解决方案
4. 商业模式
5-8. 应用价值（先进性/实效性/示范性）
9. 团队介绍
10. 其他材料

### Step 5：材料清单

每提交一个项目，在 Synthos-competition 目录下新建 `competition-YYYY/` 目录，包含：

- `申报书_已填写.docx/.pdf` — 最终的申报书
- `建设说明书.md` — 智能体/平台技术描述
- `演示脚本.md` — 视频/路演脚本
- `submission-summary.json` — 材料清单与评分对标

### 数据引用铁律

> 凡数必源。Synthos 的轮次、评分、技能数必须从 evolution-state.json 实时提取，不可凭记忆或之前的申报材料填写。

```python
# 正确做法：实时读取
with open('/media/yakeworld/sda2/Synthos/evolution-state.json') as f:
    state = json.load(f)
cycle = state['cycle']          # 当前轮次
score = state['overall_score']  # 当前评分
version = state['version']      # 当前版本
```

## 参考文件

- `references/data-elements-competition-2026.md` — 数据要素×大赛 2026年申报书填写经验：字段映射、表中各部分字数限制、合并单元格处理方式、赛道选择策略。

## 相关技能

- `writing` — 父级写作技能目录
- `political-proposal` — 同类中文正式文书撰写经验

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
