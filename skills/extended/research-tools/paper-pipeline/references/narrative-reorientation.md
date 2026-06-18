# 叙事重定位模式（Narrative Reorientation）

> 适用场景：实验数据不支持论文原本的预期叙事方向
> 核心原则：不解释、不淡化、找到数据本身的故事

## 触发条件

当 L0.5 数据诚实验证发现以下冲突之一时：

1. **方向性错误**：论文声称"A提升了B"，实验显示"A降低了B"（FN reduction 声称+67%，实验-28%）
2. **幅度虚高**：论文声称"效果显著"，实验显示"无显著差异"或"效果微弱"
3. **数据集错位**：论文用 WBC Original 论证，实际代码跑的是 WDBC
4. **结论夸大**：论文说超越SOTA，实验显示与baseline差距<0.5%

## 模式选择

根据实验数据的实际情况，选择以下叙事重定位模式之一：

### 模式A：从"错误减少"到"不确定性集中"

**适用**：系统整体性能未超越单分类器，但灰区/不确定性路由有效

```
❌ "Our system reduces false negatives by 67%"
✅ "Our system achieves 1.22× malignant enrichment in the Gray Zone"
```

**叙事框架**：
- 不再是"AI outperform baseline"，而是"AI concentrate expert attention where it matters"
- 核心声明：系统能识别哪些病例最需要人工审核
- Limitations 中诚实讨论"on this dataset, single classifiers already near-optimal"

**模板**：
```
The system's primary contribution is not surpassing the best single classifier 
on aggregate metrics, but providing a structured mechanism for concentrating 
diagnostic uncertainty on high-risk cases. This enables a human-in-the-loop 
workflow where pathologists review the most clinically consequential subset 
of cases rather than all decisions uniformly.
```

### 模式B：从"方法创新"到"工程验证"

**适用**：提出的方法在理论上有价值，但实验效果与baseline持平

```
❌ "We propose a novel architecture that achieves superior performance"
✅ "We present an engineering validation of cascade 3WD architecture for clinical triage"
```

**叙事框架**：
- 定位为"可行性验证"而非"性能突破"
- 强调架构设计原理和临床意义
- 用 ablation 分析说明各组件的贡献

### 模式C：从"单一指标"到"多维度权衡"

**适用**：某个指标不理想，但其他维度有显著价值

```
❌ "HCS-3WT achieves 84.76% automation rate (overstated)"
✅ "HCS-3WT achieves 79.07% automation rate with 99.35% auto-accuracy"
```

**叙事框架**：
- 把自动化率×准确率×灰区富集率作为三维权衡呈现
- 讨论不同阈值下的 trade-off 曲线
- 强调"safe automation"而非"maximum automation"

## 检测步骤

```bash
# 1. 识别LLM虚高标记
grep -oP '84\\.76|67%|100%|99\\.99|0\\.[0-9]{4}' paper.tex | sort -u

# 2. 提取实验数值方向
python3 -c "
import json, glob
for f in glob.glob('experiment/*.json'):
    d = json.load(open(f))
    h = d.get('hcs3wt', d)
    print(f'{f}: FN reduction = {h.get(\"fn_reduction_pct\",\"N/A\")}%')
    print(f'  Auto rate = {h.get(\"automation_rate\",\"N/A\")}%')
"

# 3. 判断方向是否一致
# 如果论文说"decrease"但实验FN reduction为负值 => 方向冲突
```

## 实战案例

| 论文 | 原叙事 | 实验发现 | 重定位后叙事 |
|:-----|:-------|:---------|:-------------|
| HCS-3WT | "FN减少67%" | FN增加28% | "灰区恶性富集1.22×" |
| (其他案例补充中) | | | |
