# EVIDENCE_SCHEMA.md — Citation Function Classifier

> 对应原则：P0（证据可溯性）
> 理论来源：Meyer (2010) "Rhetorical Functions in Research Articles"; Belcher (2009) "Writing Your Journal Article in Twelve Weeks"; Swales & Feak (2012) "Academic Writing for Graduate Students"

## 引用功能分类体系（6 类）

每篇参考文献在 Introduction 中必须标注其**功能**，而非仅标注"被引用"。

| 功能代码 | 名称 | 定义 | 关键词模式 |
|----------|------|------|------------|
| **BG** | Background | 定义领域范围、基本概念、背景知识 | "is defined as", "commonly refers to", "the field of" |
| **SUP** | Support | 支撑前文论断 | "has shown", "demonstrates", "found that", "establishes" |
| **CMP** | Contrast | 对比不同方法/观点 | "in contrast", "however", "unlike", "differs from", "on the other hand" |
| **GAP** | Gap Identification | 指出研究空白/局限 | "remains unclear", "has not been studied", "little attention", "few studies" |
| **METH** | Methodology | 说明方法来源/基础 | "following the approach of", "based on the method", "using the framework" |
| **OBJ** | Objective | 引出本文目标/动机 | "we propose", "this paper aims to", "here we show" |

## 引用功能分布质量标准

一篇合格的 Introduction 中，6 类功能的合理分布：

| 功能 | 推荐比例 | 说明 |
|------|----------|------|
| BG | 20-25% | 足够的领域背景 |
| SUP | 20-25% | 足够的支持性证据 |
| CMP | 10-15% | 对比分析（体现批判性） |
| GAP | 15-20% | 明确的研究空白 |
| METH | 10-15% | 方法学基础 |
| OBJ | 10-15% | 本文目标 |

**硬检查**：
- 任何功能占比 < 5% 或 > 40% 触发警告
- 缺少 GAP（< 1 篇论文）→ 不合格
- 缺少 CMP → 警告（无批判性对比）
- BG > 50% → 警告（背景过多，论证不足）
- SUP > 40% → 警告（单纯罗列，无 gap）

## 传递规则

每个 Citation 的 evidence 节点标注其功能代码：
```json
{"source_type": "citation_function", "source_ref": "paper_id", "function_code": "GAP", "context": "No study has examined..."}
```
