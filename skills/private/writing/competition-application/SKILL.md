---
name: competition-application
description: 确认赛道后，在申报书表格中标记"√已选：XXX"。
signature: 'competition-application -> writing: synthetic skill for competition application'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 确认赛道后，在申报书表格中标记"√已选：XXX"。
    signature: 'competition-application -> writing: synthetic skill for competition application'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

-|
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
- [ ] 申报主体（医院/临床/科研实验室/高校/科研院所）已排除“数据基础设施”赛道，避免需填营收/融资/Token消耗等财务数据
- [ ] 确认赛道后在申报书表格对应位置标记“√已选：XXX”
- [ ] 叙事采用“痛点（Pains）-方案（Solution）-成效（Results）”三层结构，各层引用具体数据
- [ ] 关键数据（轮次、评分、技能数）从 evolution-state.json 实时提取（cycle/overall_score/version），未凭记忆或旧材料填写
- [ ] DOCX 合并单元格仅写入一个非合并单元格，或写入后清空传播内容
- [ ] 长文本先写入 JSON 再经脚本读取填充至对应段落索引，规避 Python 编码问题
- [ ] 定位长文本段落前已打印所有段落确认索引，且内容紧跟标题段落
- [ ] 已清除模板残留说明文字（“（介绍参赛项目的背景...）”等）
## 核心原则 · PRINCIPLES
1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证
## Golden 集合 · GOLDEN SET
- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
# Competition Application---
> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Competition Application
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[COMP-001]** 申报主体为医院/临床/科研实验室或高校/科研院所 → 避免选择“数据基础设施”赛道，因该赛道需填写营收/融资/Token消耗等财务数据
- **[COMP-002]** 确认赛道选择后 → 在申报书表格对应位置标记“√已选：XXX”
- **[COMP-003]** 构建项目叙事结构时 → 采用“痛点（Pains）- 方案（Solution）- 成效（Results）”三层通用模板
- **[COMP-004]** 填充 DOCX 表格遇到合并单元格（merged cells） → 仅写入一个非合并单元格或写入后清空传播内容，防止内容错误扩散
- **[COMP-005]** 处理长文本写入或 Python 编码问题 → 先将文本写入 JSON 文件，再由脚本读取 JSON 填充至对应段落索引
- **[COMP-006]** 引用轮次、评分、技能数等关键数据 → 必须从 evolution-state.json 实时提取，严禁凭记忆或旧材料填写
- **[COMP-007]** 定位申报书长文本段落 → 先打印所有段落确认索引，确保内容紧跟在标题段落之后
- **[COMP-008]** 完成内容填充后 → 清除模板中残留的“（介绍参赛项目的背景...）”等说明性文字