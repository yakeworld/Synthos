---
name: competition-submission
description: zip -r submission.zip submission/ -x "*/.*"
signature: 'competition-submission -> content-production: synthetic skill for competition
  submission'
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
    description: zip -r submission.zip submission/ -x "*/.*"
    signature: 'competition-submission -> content-production: synthetic skill for
      competition submission'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

## IO_CONTRACT

- **input**: 竞赛要求 — 赛道、评分维度、格式要求、截止时间、申报表模板
- **input**: 项目素材 — 技术方案、代码、演示数据（用于填充模板）
- **output**: submission.zip — 技术规格书/路线图(Mermaid)/视频脚本/申报表(docx)/答辩PPT(pptx) 打包件
- **output**: 完整性检查结论 — 是否涵盖所有评分维度/格式要求/截止时间

## 原则 (Principles)

- **循式而作**：规格书、路线图、脚本、申报表、答辩 PPT 各有既定模板，循式而作方可保证齐备。
- **以评为纲**：材料取舍以评分维度与格式要求为纲，不循纲则完备性无从谈起。
- **打包必核**：`zip -r submission.zip submission/ -x "*/.*"` 之末必查评分维度、格式与时限俱齐，勿留遗漏。
- **素材先于格式**：技术方案、代码、演示数据为纲，格式为末；纲不正则格式愈工愈谬。

--|
| 技术规格书 | `references/tech-spec-template.md` | Markdown |
| 路线图 | `references/roadmap-template.md` | Mermaid timeline |
| 视频脚本 | `references/video-script-template.md` | 分镜脚本格式 |
| 申报表 | `references/form-filling-guide.md` | python-docx/pdf |
| PPT | `references/presentation-template.md` | python-pptx |

详见各模板文件。

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[COMP-001]** 存在既定模板（规格书/路线图/脚本/申报表/PPT） → 严格遵循各文档的既定模板格式进行内容填充，确保结构齐备
- **[COMP-002]** 面对材料取舍与内容规划 → 以评分维度与格式要求为最高纲领，确保所有材料直接回应评分标准
- **[COMP-003]** 执行最终打包操作（zip） → 在打包完成后立即执行完整性检查，确认涵盖所有评分维度、格式要求及截止时间
- **[COMP-004]** 处理技术方案、代码与演示数据 → 优先确保核心素材（纲）的正确性与完整性，再处理格式美化（末）
- **[COMP-005]** 生成技术路线图 → 使用 Mermaid timeline 语法生成可视化路线图以符合特定格式要求
- **[COMP-006]** 生成申报表文档 → 使用 python-docx 或 PDF 工具链生成符合中国申报表规范的文档
- **[COMP-007]** 生成答辩 PPT → 使用 python-pptx 库基于标准模板生成演示文稿

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

- [ ] 五类材料（技术规格书/路线图/视频脚本/申报表/答辩PPT）均按 `references/` 对应模板生成，结构齐备（COMP-001、循式而作）
- [ ] 每项材料内容直接回应评分维度与格式要求，材料取舍以评为纲，无离纲内容（COMP-002）
- [ ] 核心素材（技术方案、代码、演示数据）先于格式校验完整正确，格式美化未掩盖素材缺陷（COMP-004、素材先于格式）
- [ ] 路线图采用 Mermaid timeline 语法且渲染无误（COMP-005）
- [ ] 申报表经 python-docx/PDF 工具链生成并符合中国申报表规范，PPT 经 python-pptx 基于标准模板生成（COMP-006/007）
- [ ] `zip -r submission.zip submission/ -x "*/.*"` 执行后，包内实际包含全部五类产物，无多余文件、无 `*/.*` 隐藏文件（COMP-003、打包必核）
- [ ] 完整性检查确认涵盖所有评分维度、格式要求，并核对当前时间早于竞赛截止时间（Step 4-5）

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 竞赛通知（赛道 + 3 项评分维度 + 格式要求 + 截止时间）+ 就绪的核心素材（技术方案、代码、演示数据）+ `references/` 下五套模板（tech-spec/roadmap/video-script/form-filling/presentation）
- **Golden Output**: `submission.zip` 满足三项硬断言：① 解包后恰含五类产物（技术规格书/路线图/视频脚本/申报表 docx/答辩 PPT pptx），无多余文件、无 `*/.*` 隐藏文件；② 路线图用 Mermaid timeline 语法且渲染无误，申报表经 python-docx、PPT 经 python-pptx 基于标准模板生成；③ 完整性检查逐项打勾确认涵盖全部评分维度与格式要求，且当前时间早于截止时间
- **Golden Error**: 完整性检查发现评分维度/格式要求缺项，或当前时间已晚于竞赛截止时间 → 应输出带缺项清单的完整性检查结论并拒绝交付 `submission.zip`，而非静默打包交付；或解包核对发现隐藏文件混入（`-x "*/.*"` 未生效）→ 报"包内含隐藏文件"并重建打包命令

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Competition Submission---
> (P032 去重: 保留第二份 1 行独有内容)
# Competition Submission

## 示例 · EXAMPLES

1. **输入**：某竞赛通知给出赛道、3 项评分维度、docx 申报表模板与截止时间（COMP-002 以评为纲）→ **操作**：按 COMP-001 循式而作，用 `references/` 下五套模板生成技术规格书、Mermaid timeline 路线图（COMP-005）、视频脚本、申报表、答辩 PPT → **验证**：逐项对照评分维度打勾，无离纲内容（COMP-002；VERIFICATION 第 2 项）。
2. **输入**：核心素材（技术方案、代码、演示数据）已就绪，格式待美化 → **操作**：按"素材先于格式"原则先校验技术方案与演示数据完整性，再用 python-docx/python-pptx 生成申报表与 PPT（COMP-006/007）→ **验证**：格式美化未掩盖素材缺陷；Mermaid 渲染无误（COMP-005、VERIFICATION 第 3/4 项）。
3. **输入**：五类产物齐备待交付 → **操作**：执行 `zip -r submission.zip submission/ -x "*/.*"` 后按 COMP-003 打包必核：解压核对包内恰含五类产物、无隐藏文件 → **验证**：完整性检查确认涵盖全部评分维度与格式要求，且当前时间早于截止时间（VERIFICATION 第 6/7 项）。