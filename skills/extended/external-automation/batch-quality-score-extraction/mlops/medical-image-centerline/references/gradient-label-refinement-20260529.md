# 梯度引导标签精炼实验记录 (2026-05-29)

## 核心思路

SCC骨迷路的CT边界梯度极强（~1000 HU落差→全身最锐利边界之一），可作为自监督信号：
- 将预测/手工标签的边界向CT图像梯度峰值方向拉拢
- 不依赖额外标签，仅用CT图像本身的梯度信息

## 算法

```python
对标签边界上每个体素p:
    window = p附近3x3x3搜索窗
    q* = argmax_{q in window} G(q)  # 梯度峰值
    if distance(p, q*) <= search_radius and G(q*) > threshold:
        将p移动到q* → 边界对齐梯度脊
    else:
        保留p → 梯度不可信
从移动后的边界点云重新水填充 → 精炼标签
```

## 实验设计：三种场景

### Scenario A: 人造缺陷 → 修复 (验证算法有效性)

| 步骤 | 操作 |
|:-----|:-----|
| 1 | 用label_B_downsampled的精修标签作为GT |
| 2 | 腐蚀2体素制造"粗糙标签" (Dice vs GT=0.29) |
| 3 | 梯度精炼 → Dice提升至0.60 (+0.31) ✅ |

**结论**: 大幅偏移的边界，梯度能有效拉回。9/9 case改善。

### Scenario B: A(手工) → 梯度精炼 → 对比B(精修) (真实临床场景)

| 步骤 | 操作 |
|:-----|:-----|
| 1 | A标签 (手工标注, n=9) as 输入 |
| 2 | B标签 (专家精修, n=9) as 参考标准 |
| 3 | 梯度精炼A → 对比B (Dice从0.857降至0.712) ❌ |

**结论**: 0/9 case改善。A与B差异为 **解剖知识驱动**（专家修正），而非梯度驱动。

**根因分析**:
- A手工标签的BGA(边界梯度对齐度)=0.93（已有分析数据），已高度对齐
- 在0.488mm临床CT分辨率下，梯度峰值±2体素的噪声级移动不可分辨
- A标签与B标签的Dice=0.857已足够高，剩余误差是解剖判断差异

### Scenario C: nnU-Net预测 → 梯度后处理 (待验证)

根据已有BGA分析数据：
- C (M_A预测): BGA=0.9497
- D (M_B预测): BGA=0.9059
- 预测的边界梯度和手工标签几乎一样好，梯度精炼的边际收益预计有限

## 关键参数

| 参数 | 推荐值 | 说明 |
|:-----|:-------|:-----|
| search_radius | 2-3 voxels | 移动范围限制，过大导致异常偏移 |
| grad_threshold_ratio | 0.15-0.20 | 梯度阈值 = 标签内梯度中位数 × 此比例 |
| 适用分辨率 | ≥0.488mm | 高分辨CT(0.156mm)骨内梯度噪声大，不使用 |

## 论文角度建议

**正确定位**: 梯度精炼作为**粗分割后处理**（如全自动nnU-Net预测 → 边界微调），
而非**手工标签替代精炼手段**。

**不适用的场景**: A→B级精修（专家解剖知识不可被梯度替代）。

## 代码位置

- `/media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/code/gradient_refine_ct.py`
  — Scenario A验证脚本（人造缺陷→修复）
- `/media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/code/gradient_refine_ab.py`  
  — Scenario B验证脚本（A手工→梯度→对比B）
- 输出JSON: `.../data/gradient_refine/results_clinical_ct.json` 和 `results_A_vs_B.json`
