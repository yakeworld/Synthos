# XHS: 质检报告类帖子的源文件选择

## 问题

用户说"pima文献质量报告"时，容易错误地打开数据完整性审计报告(如paper-numerical-integrity-audit)，但用户要的是文献/引用质量报告。

## 正确映射

| 用户说... | 看这个文件... | 不打开这个 |
|:----------|:--------------|:----------|
| "文献质量报告" / "质检报告" | 07-quality/layer-b-qc.md, quality-report.md, qc-d8-refs.md | paper-numerical-integrity-audit |
| "数据完整性" / "L0.5" | 07-quality/quality_check.md (G6实验数据) | 文献类报告 |
| "D8/D10a" | 07-quality/qc-d8-refs.md | 所有其他 |
| "引用质量" | 07-quality/reference_verification_report.md | 数据审计 |

## Pillow信息图生成步骤

质检报告→配图的标准流程:

1. 读源文件提取关键数值 (D8, D10a, 综合分, 各维度)
2. 写Pillow脚本, 深色背景 #0F172A
3. 画4张2列卡片 (通过=绿, 警告=橙, 不通过=红)
4. 画评分进度条 + 逐维度列表
5. 底部辅助卡片 + footer
6. 输出1080×1440 PNG

颜色值: 通过 (0,255,170), 警告 (255,169,77), 不通过 (255,107,107)
