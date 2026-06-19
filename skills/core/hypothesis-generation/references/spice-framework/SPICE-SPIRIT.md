# SPICE/SPIRIT 研究问题框架

> 理论来源：Thompson (2004) "Defining and formulating your research question"; Richardson (1999)

## SPICE 框架

SPICE 是临床和研究问题形式化的标准框架。将 Gap 转化为可操作的研究问题：

```
SPICE:
  S — Setting (研究场景): 在哪里做？人群/环境/机构？
  P — Perspective (视角): 谁的角度？患者/医生/政策制定者？
  I — Intervention (干预): 什么干预/方法/技术？
  C — Comparison (对照): 与什么比较？标准治疗/安慰剂/现有方法？
  E — Evaluation (评估): 评估什么指标？结局/效果/成本？
  (C) — Context (背景): 背景因素 (非核心但重要)
```

### 每个要素的强制要求

| 要素 | 必须包含 | 示例 |
|------|----------|------|
| **Setting** | 具体的场景/人群定义 | "三级医院眼科门诊的 BPPV 患者" |
| **Perspective** | 明确视角方 | "临床医生" 或 "患者报告结局" |
| **Intervention** | 具体可操作的干预 | "VOR-Kappa 3D 校准算法 v2.0" |
| **Comparison** | 明确的对照 | "传统 2D Kappa 校准方法" |
| **Evaluation** | 可量化的评估指标 | "校准误差 (度), 可重复性 (ICC), 耗时 (秒)" |

## SPIRIT 框架 (更广泛的研究设计)

SPIRIT 适用于非干预性研究 (观察性/仿真/质性):

```
SPIRIT:
  S — Source (数据来源): 数据从哪里来？
  P — Phenomenon of Interest (研究现象): 研究什么现象？
  I — Research design (研究设计): 如何设计？
  T — Types of outcome (结局类型): 测量什么？
  (timing) — 时间框架: 随访期/观察期/实验期
```

## 从 Gap 到 Research Question 的转换

```
Step 1: 输入 — 空白类型 (来自 GAP-TYPE.md)
  → 方法空白/理论空白/实证空白/应用空白

Step 2: 填充 SPICE 模板
  → 每个要素从空白中提取或推断

Step 3: 形成研究问题
  → "在 [Setting] 中，[Perspective] 认为 [Intervention] 相比于 [Comparison] 在 [Evaluation] 上是否有改进？"

Step 4: 质量检查
  → 每个要素是否具体？是否可操作？是否可测量？
```

## 不合格标准

```
1. 任何核心要素 (S/P/I/C/E) 缺失 → FAIL
2. Setting 过于模糊 (如"医院") → WARNING
3. Intervention 不可操作 → FAIL
4. Evaluation 无量化指标 → FAIL
5. Comparison 缺失 (单臂研究需说明理由) → WARNING

合格研究问题必须:
- 包含所有 5 个核心要素
- 每个要素有具体定义
- 可转化为可检验的假设
```

## 示例

```
Gap: "现有 VOR 校准方法未考虑 3D 空间旋转"

SPICE:
  Setting: 前庭功能检查实验室
  Perspective: 临床神经耳科医生
  Intervention: VOR-Kappa 3D 校准算法
  Comparison: 传统 2D 校准方法
  Evaluation: 角度误差 (度), ICC (可重复性), 诊断灵敏度

Research Question:
  "在 前庭功能检查实验室 中，临床医生认为 VOR-Kappa 3D 校准
   算法 相比于 传统 2D 校准方法 在 角度误差、可重复性和诊断灵敏度
   上是否有改进？"

→ 转化为假设: H₁: 3D 校准的角度误差 < 2D 校准 (p<0.05)
```

## 理论来源

- Thompson, K. (2004). "Defining and formulating your research question." *Chemistry Centre Journal*, 1(1), 5.
- Richardson, J. T. E. (1999). "Variables and research designs: the use of SPICE as an alternative to PICO." *Journal of Further and Higher Education*, 23(3), 380-388.
