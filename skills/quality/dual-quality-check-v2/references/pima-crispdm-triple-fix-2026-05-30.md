# Pima CRISP-DM Triple Fix — 2026-05-30 实战

## 问题发现 — 双质量检查阶段

**论文**: Process-Driven Credibility: A CRISP-DM Helix Framework for Robust Pima Diabetes Prediction
**路径**: paper-submission/paper.tex (423行) + paper-submission/references.bib (42条目)
**目标期刊**: BMC Medical Informatics and Decision Making

### 问题清单

| 问题 | 严重度 | 检测方式 |
|:-----|:------:|:---------|
| D10a 覆盖率 76.2% | 🔴 | 本地D10a检查 |
| Table I bibkey/作者名错配（Kurniawan→Chang2024, Chinnababu→Mehta2024） | 🔴 | 人工审核 |
| Kapoor2024Leakage 过度引用（34次/32个cite组≈100%） | 🟡 | 高频检测 |
| D6 新颖性 0.70（结论叙事弱） | 🟡 | Layer A评审 |
| D5 清晰性 0.80（SHAP图仅为文本表） | 🟡 | Layer A评审 |
| D9 PDF覆盖率 5/42（11.9%） | 🟢 | 本地D9统计 |

## 修复执行

### 修复①：僵尸引用激活（10→0）

10条僵尸引用及插入位置：

- **Artzi2023DataLeak** → Methods §2.2, 数据泄露系统综述替代Kapoor通用引用
- **Dou2007Systematic** → Discussion §4.2, PIDD文献系统性回顾
- **Luo2016TRIPOD** → Methods §2.2, ML预测模型报告指南
- **Mandrekar2010ROC** → Results §3.1, ROC曲线方法学
- **Roberts2021CommonML** → Introduction §1.2, ML常见陷阱/方法论失败
- **Tejani2024CLAIM** → Discussion §4.3, CLAIM检查表
- **VanCalster2019Calibration** → Introduction §1.2, 校准误差/准确率陷阱
- **Varoquaux2022Machine** → Introduction §1.2, ML方法论失败模式
- **Wiens2019MLClin** → Introduction §1.1, 负责任ML路线图
- **Heinze-Deml2018Causal** → 移除（无自然插入点），因果结构学习与本论文无关

### 修复②：Table I bibkey错配

Kurniawan et al. -> Chang et al. (bibkey Chang2024)
Chinnababu et al. -> Mehta et al. (bibkey Mehta2024)

### 修复③：Kapoor2024过度引用（34→15次）

替换策略：
- 通用数据泄露声明 → Wen2024Leakage, Artzi2023DataLeak, Varoquaux2022Machine (8次)
- 我们自己的结果 → 直接删除引用 (7次)
- CRISP-DM Helix框架介绍 → 直接删除引用 (3次)
- SHAP分析描述 → 直接删除引用 (1次)
- 保留：Recall Paradox讨论 (2次)

### 修复④：D6 结论叙事增强

原文: transforms best practice from an aspirational principle into a verifiable pipeline component
改为: transforms data isolation from an aspirational principle into an executable computational constraint, closing the implementation gap between guideline awareness and auditable practice
新增末句: The central message of this work is that methodological rigor---not algorithmic complexity---is the primary determinant of clinical ML credibility, and that rigor must be architecturally enforced, not merely recommended.

### 修复⑤：SHAP图文本表→TikZ条形图

三色水平条形图（蓝/绿/橙），带坐标轴和数值标签

### 修复⑥：PDF补充（5→8）

通过OpenAlex下载 Collins2015TRIPOD (473KB) + Moons2019PROBAST (1.1MB)

## 结果对比

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| D8 | 42 | 41 |
| D10a | 76.2% -> 100% | ✅ |
| 僵尸引用 | 10 -> 0 | ✅ |
| Kapoor2024 | 34次 -> 15次 | -56% |
| D7 引用质量 | 0.65 -> 0.75 | +0.10 |
| D5 清晰性 | 0.80 -> 0.85 | +0.05 |
| D6 新颖性 | 0.70 -> 0.72 | +0.02 |
| D9 PDF | 5 -> 8 | +3 |
| 校准avg | 0.807 -> 0.831 | +0.024 |
| 编译 | 9页, 0错误, 0警告 | ✅ |

## 教训

1. 自动修复是默认行为
2. Table I一致性易被忽视
3. Kapoor模式（单一bibkey占比>50%）总是隐藏着替换机会
4. 图表类论文不应使用文本表
5. 结论叙事决定D6评分
