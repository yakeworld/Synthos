# 引用功能分类器

> 理论来源：Meyer (2010) "Rhetorical Functions in Research Articles"; Belcher (2009); Swales & Feak (2012)

## 引用功能分类（6 类）

每篇参考文献在 Introduction 中必须有**功能标注**：

| 代码 | 功能 | 定义 | 检测模式 |
|------|------|------|----------|
| BG | Background | 提供领域背景、定义、基本概念 | "is defined as", "commonly", "in the field of" |
| SUP | Support | 支撑前文论断 | "has shown", "demonstrates", "found that", "establishes" |
| CMP | Contrast | 对比不同方法/观点 | "in contrast", "unlike", "differs from", "on the other hand" |
| GAP | Gap | 指出研究空白/局限 | "remains unclear", "has not been studied", "few studies" |
| METH | Methodology | 说明方法来源/基础 | "following the approach of", "based on", "using the framework" |
| OBJ | Objective | 引出本文目标/动机 | "we propose", "this paper aims to", "here we show" |

## 引用功能分布质量标准

```
合理分布（全部满足才合格）:
- BG:     20-25% ✓
- SUP:    20-25% ✓
- CMP:    10-15% ✓
- GAP:    15-20% ✓
- METH:   10-15% ✓
- OBJ:    10-15% ✓

硬检查:
- GAP 缺失 (< 1 篇):          FAIL
- CMP 缺失 (无对比):          WARNING
- BG > 50%:                  WARNING (背景过多)
- SUP > 40%:                 WARNING (单纯罗列)
- 任何功能 < 5%:             WARNING
- 任何功能 > 40%:            WARNING
```

## 传递规则

```json
{"source_type": "citation_function", "source_ref": "paper_id", "function_code": "GAP", "context_snippet": "No study has examined..."}
```
