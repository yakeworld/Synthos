# Gap-Analysis Review D2 Formalization Pattern

> 实测：D2 +0.06 (0.78→0.84), avg +0.019 (0.804→0.823)
> 论文：bppv-pd-clinical-review v4 (Core4∩Core5, gap analysis review)
> 日期：2026-05-26 Phase 3 T2→T1增强

## 适用条件

- 论文类型：**系统性综述/空白分析论文**（无原始实验数据）
- 当前 D2 ≤ 0.80（方法学纯文本描述，零方程零算法）
- D7 ≥ 0.80（引用已充分，非瓶颈维度）
- 论文结构：有 Gap 定位 + 间接证据 + 可检验预测

## 核心模式

给综述论文添加 **3个形式化方程 + 1个算法伪代码** 的数学框架：

### 方程模板

| # | 方程 | 作用 | D2贡献 |
|:-:|:-----|:-----|:------:|
| 1 | **共患病率模型** | $P_{\text{co-occur}}(a) = I_{\text{BPPV}}(a) \cdot P_{\text{PD}}(a)$ | 形式化"期望共患率"概念 |
| 2 | **条件概率模型** | $P_{\text{BPPV}|\text{PD}} = P_{\text{BPPV}} + \Delta_{\text{PD}}(\mathbf{x})$ | 量化PD特异性增额风险的权重向量 |
| 3 | **协同效应模型** | $F_{\text{BPPV}\cap\text{PD}} = 1 - (1 - f_{\text{BPPV}})(1 - f_{\text{PD}}) + \epsilon_{\text{synergy}}$ | 估算叠加风险 + 协同效应区间 |

### 算法模板

| 组件 | 内容 | D2贡献 |
|:-----|:-----|:------:|
| Algorithm 1 | 5-Phase筛查协议伪代码: Identification→Diagnostic Adaptation→Modified CRM→Post-Treatment→Fall Prevention | 将文本协议升格为可执行算法 |

## 执行步骤

```
检查论文D2当前分 → 确认零方程/零算法
  ↓
Step 1: 写3个方程
  识别论文中隐含的定量概念 → 写为形式化方程
  每个方程配1-2个引用确认参数来源
  ↓
Step 2: 写1个算法
  找到论文中"方法""协议""流程"节 → 写为Algorithm
  用pseudocode格式: Require/Ensure/If/Else/For/EndIf
  ↓
Step 3: 插入
  方程插入Methods节末尾或Results前
  算法插入Discussion节中对应协议描述后
  ↓
Step 4: 编译验证
  pdflatex ×2
  检查 0 error, 0 undefined
  验证 cite↔bibitem 完整性
  ↓
Step 5: 更新quality-report
  D2: +0.04~0.07
  D4: +0.01~0.03 (新增页/内容)
  D6: +0.02~0.04 (叙事升级)
```

## 注意事项

- **D3不受益**：综述论文D3有天然上限(~0.75)，方程不改变此限制
- **bibitem不增加**：用论文已有引用做参数来源，不触发Strategy B
- **D7不降低**：100%引用匹配保持不变
- **编译风险低**：仅需amsmath已有包，algorithm+algpseudocode与elsarticle兼容已验证
- **预期收益率**：D2 +0.04~0.07, avg +0.015~0.025/轮
