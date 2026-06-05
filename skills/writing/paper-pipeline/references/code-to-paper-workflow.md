# Code-to-Paper 快捷管线

> 当实验代码（Jupyter notebook / Python脚本）已存在时，绕过P1完整文献检索，直接进入P2写作。
> 适用条件：代码已验证可运行、核心方法已建立、只需论文化。

## 触发条件

| 条件 | 判定 |
|:-----|:------|
| 代码中存在核心数学公式/算法 | 是 → 用Code-to-Paper |
| 已有实验结果数据（JSON/CSV/图表） | 是 → 跳过NotebookLM逐问法 |
| 代码中有明确的创新点/方法 | 是 → 直接提取并写入 |
| 文献综述已在其他论文中覆盖 | 是 → 复用已有.bib |

## 三阶段流程

### Phase 1: 代码审计

扫描notebook提取三类内容：
- Markdown cell → 方法描述
- Code cell → 公式、参数、算法伪代码
- Output cell → 实验结果（数值/图表）

**产出**: methods-extracted.md

### Phase 2: 论文生成

直接从提取的方法写LaTeX：
- 用`elsarticle`模板
- 公式/参数直接从代码提取
- 引用复用已有.bib
- 用delegate_task或直接写paper.tex

### Phase 3: 验证

- 编译: pdflatex → bibtex → pdflatex × 2
- 0 undefined refs = 通过
- Layer A评估D3(实验验证)是否充分

## 适用场景

| 代码类型 | 论文产出 | 案例 |
|:---------|:---------|:-----|
| 3D几何建模 | 方法学论文 | eye_modelv3 → 角膜屈光校正 |
| 图像分割 | 算法论文 | DeepVOG → 瞳孔分割 |
| 物理仿真 | 仿真论文 | epley.ipynb → BPPV复位 |
| 数据分析 | 方法论文 | pupil_math → 双椭圆拟合 |

## 陷阱

- 缺真实数据验证时D3偏低(~0.78)
- 代码placeholder图需替换为真实结果
- 代码输出需可复现 → 附复现脚本

## 实战记录

2026-06-05: `3d-pupil-localization` 论文从 3 个 Jupyter notebooks 创建：
- eye_modelv3.ipynb (角膜屈光)
- pupil_math.ipynb (双椭圆拟合)
- geteyeballv1.ipynb (3D眼球模型)
→ 18页PDF, 301KB, 0编译错误, 35篇引用
