# 评估工具充分性分析 — Measurement Tool Adequacy

> 用于标书评审：检查提案所用的测量工具是否能够充分捕获其声称要测量的结局变量。

## 核心问题

**常见模式**：标书声称要预测XX并发症，但使用的预测变量是主观量表+简单实验室指标，与结局变量的生理本质不匹配。

**检查步骤**：

1. 解析"结局变量"的生理/病理本质（它是什么生理事件？）
2. 列出标书提出的测量工具
3. 判断每个工具测量的是"症状感知"还是"生理功能"
4. 如果所有工具都停留在"症状感知/量表层面"，而结局是生理事件→标记为严重缺陷

## 常见评估工具缺陷模式

### 模式1：用问卷测量生理事件
- **例**：用EAT-10（自报问卷）+饮水试验（看有无呛咳）来预测误吸
- **根本问题**：30%的隐性误吸患者没有咳嗽反射，饮水试验的终点判据"有无呛咳"对这些患者无效
- **文献证据**：Ponsoni et al. 2024 (Arq Neuropsiquiatr) — EAT-10在PD中检测误吸的敏感性71.42%、特异性仅45.45%

### 模式2：标书自相矛盾
- **常见**：立项依据中说"现有量表不够"，研究方法却照用同一套量表
- **检查**：标书的"不足之处"论述中提到的缺陷，是否在后面的研究方法中得到解决

### 模式3：间接推理链过长
- **例**：凝血时间→出血风险→营养状态→肺炎风险 （4层间接）
- **问题**：信噪比极低，不构成有意义的预测

## PubMed验证搜索模式

当怀疑标书的测量工具不充分时，用以下PubMed搜索模式验证：

### 搜索1：筛查工具 vs 金标准的诊断准确性
```
(("{tool_name}"[tiab] OR "{tool_abbrev}"[tiab]) AND 
(dysphagia OR aspiration OR pneumonia) AND 
(FEES OR VFSS OR videofluoroscopy OR "diagnostic accuracy" OR sensitivity))
```
- **用途**：查看某量表/测试与金标准的对照
- **例**：EAT-10在PD中的敏感性/特异性 → PMID: 38325386

### 搜索2：补充客观指标的文献证据
```
(("{objective_measure}"[tiab]) AND 
(aspiration OR dysphagia) AND 
(Parkinson* OR elderly OR geriatric) AND 
(predict* OR risk OR assessment))
```
- **用途**：寻找可补充的客观指标（咳嗽峰流速、RSST、SpO2监测等）
- **例**：Peak cough flow for aspiration → 144篇相关文献

### 搜索3：评估工具是否在扩展/改进中
```
("{tool_name}"[tiab] OR "{water_swallow_test}"[tiab]) AND 
(extended OR modified OR improved OR enhancement OR validation)
```
- **用途**：如果学术界还在不断改进该工具，说明原版不够
- **例**：eTWST (Extended Timed Water Swallow Test) → PMID: 39521747

## 推荐补充的客观指标（床旁可操作）

| 指标 | 工具 | 成本 | 文献证据 |
|:-----|:-----|:----:|:---------|
| 咳嗽峰流速(PCF) | 手持峰流速仪 | ~50元 | 144篇文献；直接测量气道保护能力 |
| RSST反复唾液吞咽 | 计时器 | 0 | Chen 2025 (J Formos Med Assoc) — 误吸预测 |
| 饮水+SpO2监测 | 指夹式脉氧仪 | <50元 | Wakasugi 2008 (Dysphagia) — 捕捉隐性误吸 |
| 吞咽声音AI分析 | 电子听诊器+软件 | ~500元 | Nakamori 2023 (J Neurol Sci) — PD吞咽 |

## 检查清单

- [ ] 标书说"现有工具不够"→后续方案是否解决了这个问题？
- [ ] 结局变量是生理事件→预测变量是否包含客观生理指标？
- [ ] 所有预测变量都是量表/自报→标记为重大缺陷
- [ ] 引用文献是否直接支持该工具在目标人群中的诊断准确性？
- [ ] 标书声称的AUC/敏感性/特异性是否有具体文献支撑？
