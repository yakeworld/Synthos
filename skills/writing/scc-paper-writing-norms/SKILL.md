---
name: scc-paper-writing-norms
description: "SCC论文写作规范与质量流程。从SCC数学形态学论文(v4)实战提炼：09目录体系、版本追踪、数据溯源、引用验证三阶检查、BibTeX转换、双质检。适用于解剖形态学/生物力学类论文的写作管理。"
signature: "paper_topic: str -> writing_rules: dict"
allowed-tools: [terminal, file]
version: 1.5.0
tags: [writing, scc, morphology, quality, paper-organization]
related_skills: [paper-pipeline, dual-quality-check-v2, sci-paper-standard-structure, paper-reference-pipeline]
---

---

## 原理层·文言

> 「法象莫大乎天地，变通莫大乎四时。」形态之文，重数据溯源。
> 「物有本末。」一中心线，二螺旋拟合，三骨膜偏差。
> 09目录体系，版本日日新。凡数必源，不源不取。# SCC论文写作规范

## 技能调用链

开始前依次加载：

```bash
# 1. 论文全流程编排器（主skill）
skill_view(name='paper-pipeline')
# 2. 双质量检查
skill_view(name='dual-quality-check-v2')
# 3. 参考文献管线
skill_view(name='paper-reference-pipeline')
# 4. IMRaD结构
skill_view(name='sci-paper-standard-structure')
```

本技能专注于SCC论文特有的规范，不做泛化。通用流程由上述技能覆盖。

---

## 核心理念

**凡引必验，引必有据，验必有全文。**
**数据可追溯，代码可复现，声明可验证。**

---

## 一、论文目录体系（09-子目录）

（通用目录结构参考 `paper-pipeline` 技能，以下是SCC特有的目录约定）

```
papers/{paper-name}/
├── 01-manuscript/        ← 主稿 (.tex, .pdf, README.md, DATA_MAP.md)
├── 02-submission/        ← 投稿包 (manuscript.pdf, cover-letter, declarations, figures/)
├── 03-code/              ← 分析代码 + data/ (含 .mrk.json 中心线文件)
├── 04-data/              ← 拟合参数 .csv, Bootstrap结果 .json
├── 05-figures/           ← 出版级Figure (PDF矢量，6×3布局优先)
├── 06-references/        ← pdfs/ + REFERENCE_MANIFEST.md
├── 07-quality/           ← 质量报告 (ref-audit-report.md, qc*.md)
├── 08-records/           ← CHANGE_LOG.md, TODO.md, RESEARCH_GAPS.md
└── 09-background/        ← 外部相关材料 (article_todo副本等)
```

### 目录初始化

```bash
mkdir -p 01-manuscript 02-submission 03-code/data \
  04-data/{gradient_refine,figures_cache} 05-figures \
  06-references/pdfs 07-quality 08-records 09-background
```

---

## 二、版本管理（SCC特有）

### 文件命名

- 主稿: `{paper-name}-v{N}.tex` → `{paper-name}-v{N}.pdf`
- 最终工作版: `v{N}-paper.tex`（N=当前最大版本号）
- 提交包: `02-submission/manuscript-v{N}.pdf`

### CHANGE_LOG 模板

`08-records/CHANGE_LOG.md`：

```markdown
# 变更日志

## v4 (2026-05-30)
### 新增
- §2.3 High-Resolution Micro-CT Validation Dataset (uCT 31标本62耳)
- §3.3 Cross-Modality Validation + Figure 2 (uCT vs CT |b|箱线图)
### 修正
- Smith2021 → 删除（虚构引用）
- Damiano1996 → J Fluid Mech 307:333-372（原Ann Biomed Eng错误）
- Boselli2014 → J Biomech 47:1853-1860（原标题错误）
- Manoussaki2008数值引用: 删除无法验证的b≈0.02-0.08
### 引用统计
- 引用: 43→34篇（删除Smith, Epp, Yang, Ramprashad, Thompson, Hadrys, Salminen, Tanioka, Damiano）
- PDF全文: 34/34 = 100%
```

---

## 三、数据管理

### DATA_MAP 模板

`01-manuscript/DATA_MAP.md` 必须记录的SCC特有数据层级：

| 模态 | 数量 | 用途 | 来源路径 |
|:-----|:----:|:-----|:---------|
| 临床CT | 160例(80人×2耳) | 群体中心线(475条) | `/mnt/nfs/innerear/CT<pid>/` |
| μCT | 31标本62耳 | 模态独立性验证 | 公开数据集Wimmer2019+Sieber2019 |
| 三标本配对 | 3例(sp1/sp2/sp3) | 骨vs膜对比(Table 2) | `03-code/data/sp*_*/` |

### 三标本文件结构

```
03-code/data/
├── sp1_microct/          ← μCT + PTA染色（膜迷路可见）
│   ├── ac.mrk.json       ← 骨性AC中心线
│   ├── ac_mem.mrk.json   ← 膜性AC中心线
│   ├── data_dict.json    ← 标本元数据
│   └── LC_MEM_merged.mrk.json  ← 合并文件(见下方标注修复)
├── sp2_mrn/              ← 7T MRI（膜迷路天然可见）
├── sp3_ict/              ← 工业CT + PTA染色
└── README                ← 标注说明
```

### 标注修复记录（SCC特有坑）

膜性标注可能分裂为多个文件，必须在拟合前检查：

```bash
# 检查是否有膜性分段
ls *mem* *MEM* 2>/dev/null | sort
# 若有 ≥2 个膜性文件，检查端点距
# 端点距 < 3mm → 合并为 _merged
```

已知修复（SCC论文实战）：

| 标本 | 问题 | 修复 | 端点距验证 |
|:-----|:------|:-----|:-----------|
| sp1 μCT LC | lc_mem + lc_mem2 | LC_MEM_merged (反向拼接) | 0.22mm |
| sp3 ICT AC | AC_MEM1 + AC_MEM2 | AC_MEM_merged | 0.00mm |
| sp3 ICT PC | PC_MEM1 + PC_MEM2 | PC_MEM_merged | 0.00mm |

合并后弧比参考：膜性/骨性AC:1.10-1.22, PC:1.11-1.20, LC:1.26-1.39

---

## 四、引用验证（SCC三阶检查法）

**通用引用验证流程请加载 `paper-reference-pipeline` 的 Step 7-8。** 以下是SCC论文实战中验证的具体执行方法。

### 第1阶：整本书一致性（D10a=100%）

```python
import re
tex = open('v{N}-paper.tex').read()
bib = open('references.bib').read()
tex_cites = set()
for m in re.finditer(r'\\cite[tp]?\{([^}]+)\}', tex):
    for k in m.group(1).split(','): tex_cites.add(k.strip())
bib_keys = set(re.findall(r'@\w+\{([^,]+)', bib))
print(f"D10a: {len(tex_cites & bib_keys)}/{len(bib_keys)} = {round(len(tex_cites & bib_keys)/len(bib_keys)*100)}%")
assert len(tex_cites - bib_keys) == 0, f"Orphan cites: {tex_cites - bib_keys}"
```

### 第2阶：DOI→Crossref验证

对每个有DOI的条目，验证标题前30字匹配：

```bash
for key in $(grep -oP 'doi\s*=\s*\{\K[^}]+' references.bib); do
  title=$(curl -s "https://api.crossref.org/works/$key" | \
    python3 -c "import sys,json; d=json.load(sys.stdin).get('message',{}); print(d.get('title',[''])[0][:30])" 2>/dev/null)
  echo "$key → $title"
done
```

### 第3阶：PDF全文关键声明验证

对论文中包含数字/统计声明的 `\cite{}`，用pdftotext从PDF原文确认：

```bash
for claim in "RMSE|0.08|1.4 factor|44 labyrinths"; do
  pdftotext 06-references/pdfs/{key}.pdf - | grep -io "$claim"
done
```

---

## 五、BibTeX转换（thebibliography→.bib）

**触发条件**：论文使用 `\begin{thebibliography}...\end{thebibliography}` 手写引用。

### 转换步骤

```bash
# Step 1: 提取所有bibitem → 构建references.bib
# 每条格式: @article{key, author={}, title={}, journal={}, volume={}, year={}, pages={}, doi={}}

# Step 2: 替换tex中thebibliography
# 删除 \begin{thebibliography}...\end{thebibliography}
# 插入: \bibliographystyle{elsarticle-num} + \bibliography{references}

# Step 3: 清理多余natbib（elsarticle自带）
grep -n 'natbib' v{N}-paper.tex  # 若有额外的\usepackage{natbib} → 删除

# Step 4: 全编译链
pdflatex v{N}-paper.tex && bibtex v{N}-paper && pdflatex v{N}-paper.tex && pdflatex v{N}-paper.tex

# Step 5: 验证
grep -c 'undefined' v{N}-paper.log  # 应为0
```

### BibTeX坑（SCC实战）

| 问题 | 表现 | 修复 |
|:-----|:-----|:------|
| `\b` 被解释为退格符 | `\bibliography` → `^Hibliography` | 用直接str.replace而非re.sub |
| `elsarticle` 类natbib冲突 | Option clash for package natbib | 删除额外 `\usepackage{natbib}` |
| DOI写错 | Crossref返回不相关论文 | 每篇DOI做第2阶验证 |

---

## 六、质量检查

**通用质检流程请加载 `dual-quality-check-v2` 技能。SCC特有质检以下：**

### Layer A 本地检（SCC适用阈值）

| 维度 | 方法 | 阈值 | SCC v4实际 |
|:-----|:------|:----:|:----------:|
| D8 | `grep -c '@article' references.bib` | ≥30 | 34 ✅ |
| D10a | cite vs bib匹配 | 100% | 100% ✅ |
| D9 | `ls 06-references/pdfs/*.pdf | wc -l` | ≥80% | 100% ✅ |
| 编译 | pdflatex 0 error | 0 | 0 ✅ |

### 引用卫生专项（SCC论文铁律）

1. **0虚构引用** — 所有条目至少在2个独立数据库可查
2. **DOI→论文一致** — 每篇DOI用Crossref验证标题匹配
3. **数字声明可追溯** — 每个关键数字有PDF原文支持
4. **未发表不引** — "in preparation" / "submitted" = 删除或替换
5. **经典著作注明** — 无DOI/无PDF的经典书不列入D9统计

---

## 七、投稿包

```bash
# 同步（版本更新后立即执行）
cp 01-manuscript/v{N}-paper.pdf 02-submission/manuscript.pdf
cp 01-manuscript/v{N}-paper.pdf 02-submission/manuscript-v{N}.pdf
cp 05-figures/*.pdf 02-submission/figures/
```

### 投稿包清单

```
02-submission/
├── manuscript-v{N}.pdf     ← 最新手稿
├── manuscript.pdf          ← 覆盖版本
├── cover-letter.pdf        ← 投稿信
├── declarations.pdf        ← 作者声明
├── figures/                ← 独立图表
└── checklist.md            ← 期刊核对清单
```

---

## 十、中心线拟合方法对比 — B-spline vs 对数螺旋 vs Circle等8方法

**参见** `references/centerline-fitting-method-comparison.md` — 9种方法的系统评估结果（新增Clothoid/Euler螺旋阴性发现：最小能量曲线假设不成立）。

关键结论：B-spline（RMSE 0.05-0.08mm）最精确，且揭示MEM比BONY平滑37%；Circle补充揭示MEM比BONY不圆17%。两者互补。对数螺旋Δb在n=6小样本上方向不一致。

## 十一、3D对数螺旋拟合工作流（膜性骨性配对）

用于**配对骨膜中心线的8参数HSMM模型拟合 + 参数偏移分析**。本工作流从膜性SCC重建论文实战提炼。

### 数据源

#### .mrk.json 格式（3D Slicer标记点）

中心线点云保存在3D Slicer的Markup文件中，格式为JSON：

```python
import json, numpy as np
with open('ac.mrk.json') as f:
    d = json.load(f)
pts = np.array([p['position'] for p in d['markups'][0]['controlPoints']])
# pts shape: (N, 3), 坐标系统: LPS (mm)
```

#### 标本目录规范

```
/tmp/inner_ear_canal/
├── micro_ct/       ← 骨性: ac/pc/lc.mrk.json; 膜性: ac_mem/pc_mem/lc_mem.mrk.json
├── MRN/            ← 同上命名
└── industrial_CT/  ← 骨性: AC/PC/LC.mrk.json（大写）; 膜性: AC_MEM/PC_MEM/LC_MEM.mrk.json
```

### 拟合算法

#### 8参数3D对数螺旋模型

$$\mathbf{r}(\theta) = \mathbf{O} + \mathbf{R} \cdot \begin{pmatrix} a e^{b\theta}\cos\theta \\ a e^{b\theta}\sin\theta \\ A\sin(\omega\theta+\phi) \end{pmatrix}$$

| 参数 | 含义 | 物理意义 |
|:-----|:-----|:---------|
| $a$ | 螺旋尺度 | 起始半径(mm) |
| $b$ | 螺旋生长率 | 曲率变化速率（HSMM论文核心参数） |
| $A$ | 扭转振幅 | 出平面偏离量(mm) |
| $\omega$ | 扭转频率 | 沿弧长的扭转周期 |
| $\phi$ | 扭转相位 | 起始扭转相位 |
| $c_x, c_y, \theta_0$ | 平面内位姿 | 中心+旋转 |

#### 拟合步骤

1. **SVD平面投影**：对点云做奇异值分解，取第三主分量作为法向量
2. **2D对数螺旋搜索**：对$c_x, c_y, \theta_0$做网格搜索（3×3×4网格），Nelder-Mead精化
3. **扭转拟合**：对$A, \omega, \phi$做网格搜索（3×5×3网格），Nelder-Mead精化
4. **联合精化**：全部5参数($a,b,A,\omega,\phi$)联合Nelder-Mead优化
5. **3D RMSE计算**：拟合曲线点到原始点云的最短欧氏距离均方根

### 配对参数偏移分析

```python
# 对9对MEM-BONY拟合结果:
pairs = [('AC','Sp1'),('PC','Sp1'),('LC','Sp1'),
         ('AC','Sp2'),('PC','Sp2'),('LC','Sp2'),
         ('AC','Sp3'),('PC','Sp3'),('LC','Sp3')]

deltas = {}
for canal, sp in pairs:
    b_mem = results[f'{canal} MEM ({sp})']['b']
    b_bony = results[f'{canal} BONY ({sp})']['b']
    deltas[f'{canal}({sp})'] = b_mem - b_bony

mean_db = np.mean(list(deltas.values()))  # 膜性SCC重建论文: +0.042
```

### 实战参数范围（膜性SCC重建论文）

| 参数 | BONY范围 | MEM范围 | Δ(MEM-BONY) |
|:-----|:---------|:---------|:-----------|
| $a$ | 1.42-3.91 | 1.85-3.74 | +0.04±0.81 |
| $b$ | -0.20~+0.18 | -0.25~+0.38 | **+0.04±0.15** |
| $A$ | — | — | -0.12±0.33 |
| RMSE | 0.36-1.73mm | 0.36-1.71mm | — |

### ⚡ 中心线点序方法 — 核心陷阱（2026-06-02 新增）

**这是中心线拟合中最关键的预处理步骤。选择错误的点序方法会导致RMSE虚高2.27→0.13mm（实战数据）。**

#### 问题：两种点序方法

| 方法 | 原理 | 效果 |
|:-----|:------|:------|
| **argsort(theta)** | 按角度排序点云 | 对非凸/多圈的螺旋结构排序错误，跨圈跳跃 |
| **最近邻路径**（推荐） | 从起点出发，逐点取最近未访问点 | 保持沿管道的自然顺序，np.unwrap()展开theta单调递增 |

#### 实战效果（SCC数学形态学论文 2026-05-31）

AC bony 18 pts:  argsort RMSE=2.27mm -> nn_path RMSE=0.13mm

根因：半规管不是完美圆——当中心线在平面上有交叉/重叠的XY投影时，argsort会在角度接近处跳转到物理上不连续的点。

#### 正确流程

```python
def nearest_neighbor_path(pts):
    n = len(pts)
    visited = [False] * n; path = [0]; visited[0] = True; current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j])
                 if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists); path.append(nearest)
        visited[nearest] = True; current = nearest
    return path

# 使用（gen_all_figures.py, regenerate_all.py 已验证）:
path = nearest_neighbor_path(pts)
theta_path_order = theta_raw[path]      # 按路径顺序的theta
r_path_order = r2[path]                 # 按路径顺序的r
z_path_order = z_dev[path]              # 按路径顺序的z
theta_unwrapped = np.unwrap(theta_path_order)  # 单调递增theta
```

#### 代码库现状（需清理）

| 脚本 | 方法 | 状态 |
|:-----|:------|:-----|
| gen_all_figures.py | 最近邻路径 | 生产代码 |
| regenerate_all.py | 最近邻路径（内联函数） | 生产代码 |
| gen_composite_figure.py | 最近邻路径 | 生产代码 |
| gen_model_comparison.py | 最近邻路径 | 生产代码 |
| fit_logspiral.py | 最近邻路径（已重写） | **生产代码**（2026-06-02重写，统一方法与regenerate_all.py一致） |
| fit_logspiral_aligned.py | — | 🗑️ **已删除**（与fit_logspiral.py完全重复） |

注意：argsort在refine_2d()中仅用于中心位置搜索的初始估计（粗搜索的损失函数），不参与最终参数计算。关键在于最终拟合阶段是否用最近邻路径。

#### 验证方法

对同一中心线，两种方法各跑一次，期望nn_path的RMSE远小于argsort。

### 注意事项

1. **点序一致性**：骨性和膜性中心线的点序必须一致（同一方向），否则需用最近邻路径重排
2. **坐标系统**：不同模态的数据在各自LPS空间中，但螺旋参数对坐标系统不变
3. **短弧限制**：弧长<6mm或点数<20的拟合不可靠，应标记为边界案例
4. **RMSE解读**：0.3-0.5mm为良好，0.5-1.0mm可接受，>1.0mm需检查中心线质量
5. **与HSMM论文不冲突**：HSMM论文贡献是提出模型并证明是最优描述；配对参数偏移分析贡献是量化骨膜参数差异——完全互补

## 十、SCC实战教训速查

| 教训 | SCC论文场景 | 本技能对应预防 |
|:-----|:-----------|:--------------|
| **虚构引用** | Smith2021在所有数据库查不到 | 四-2 第2阶Crossref验证 |
| **DOI写错** | Rabbitt1993的DOI指向矿物学论文 | 四-2 第2阶标题比对 |
| **数值不可追溯** | Manoussaki2008声称b≈0.02-0.08但PDF无此数 | 四-2 第3阶PDF验证 |
| **膜性标注分裂** | sp3 ICT的AC/PC膜性分两段 | 三 标注修复记录 |
| **BibTeX `\b` 坑** | re.sub破坏 `\bibliography` | 五 BibTeX坑 第1条 |
| **natbib冲突** | elsarticle自带 + 额外\usepackage | 五 Step 3 |

---

## 九、问题申报处理流程（Self-Audit Protocol）

当收到外部审阅文档（如"文章存在的问题.docx"）或自我审计清单时，按此流程逐条核实再行动。

### 9.1 问题分类矩阵

| 类型 | 示例 | 第一反应 |
|:-----|:-----|:---------|
| 🔬 数据/拟合可靠性 | "存在两套互斥拟合" | 跑管线 → 查原始数据 → 交叉验证 |
| 📝 文本描述不准确 | "Fig 1标注six models但只有四/五种" | 读tex源码核实 |
| 📚 引用问题 | "Ref[6]不可引用" | 检查.bib + 正文调用链 |
| 🔤 术语不一致 | "micro-CT称呼混乱" | 全文grep统一命名 |
| 🔢 数字不一致 | "RMSE 0.07 vs 0.27矛盾" | 查明来源（哪个模型/哪个数据集） |
| 🖼️ 图表问题 | "Fig 4C数据来源不明" | 检查caption + 源码数据来源 |

### 9.2 拟合可靠性核实流程（SCC特有）

当有人声称"存在两套互斥拟合"时：

```\nStep 1: 运行管线\n  python3 fit_logspiral.py  → 输出6条中心线RMSE/b\n  python3 regenerate_all.py → 输出全部3标本18条线参数\n\nStep 2: 检查原始数据
  03-code/data/sp{1,2,3}_*/data_dict.json  → 确认点云完整性
  04-data/batch_logspiral_params_*.csv     → 检查极端值分布
  (重点关注: 弧长<4mm, n_pts<20, |b|>0.8, RMSE>2mm)

Step 3: 交叉验证
  管线输出 b/RMSE vs Table 2 (Tab:spiral_params) vs Abstract
  确认三者的b和RMSE同源

Step 4: 判别
  RMSE全在0.07-0.17mm范围 → "未发现两套拟合"
  RMSE出现>2mm → 检查对应标本/模态是否为低分辨率数据(MRI预期0.3-1.0mm)
  极端|b|>0.8 → 检查弧长（短弧<6mm = 边界案例，不影响主结论）
```

### 9.3 文本修复管线（LaTeX）

当确认问题后修复tex文件：

**修补工具用法（关键坑 → 2026-05-31 实战更新）**：

```
patch 中 LaTeX 反斜杠转义规则：

new_string 写 "Figure~\\ref{fig:X}"  → 文件得到 \ref（✅ 正确）
new_string 写 "Figure~\\\\ref{fig:X}"→ 文件得到 \\ref（❌ 编译为换行符+文本）

验证方法：grep后检查，不只看diff输出
例外：{\textmu} 等 LaTeX 特殊命令写法不变
```

**修复后验证链**：

```bash
# 编译两次（交叉引用）
xelatex v4-paper.tex && xelatex v4-paper.tex
grep -c "Error\|undefined" v4-paper.log  # 应为0
# 验证修改
grep "目标文本" v4-paper.tex  # 确认存在
grep "被替换文本" v4-paper.tex  # 确认不存在
```

### 9.4 多数据集命名规范

当论文使用≥2个独立数据集时，统一编号：

```
Dataset 1 = 基准/高精度数据集（如3标本多模态）
Dataset 2 = 大规模人群数据集（如160例临床CT）
Dataset 3 = 独立验证数据集（如31例uCT）
```

命名规则：
- 所有§子节标题加 "(Dataset N)" 后缀
- 所有Fig caption首次引用标注 Dataset N
- 所有结果§的段落起始明确标注数据集归属
- 避免用 "high-resolution micro-CT" 同时指代不同的数据集

### 9.5 疑似问题与误报判别

SCC论文实战经验：部分审阅意见属于"阅读惯性误读"。

| 常见误报 | 真实原因 | 应做动作 |
|:---------|:---------|:---------|
| "RMSE 0.07和0.27矛盾" | 0.07-0.17是对数螺旋，0.27是平面圆 | 在§3.1加一句话澄清 |
| "b来自失败拟合" | 实际来自RMSE=0.1326mm的可靠拟合 | 跑管线输出打印验证 |
| "Fig 1只展示4种模型" | 图实际包含6种但Fourier因尺度大被裁剪 | caption加排除说明 |
| "三例各3种模态" | 实际是3例各1种模态（误读§2.1） | §2.1明确写"each by one modality only" |

### 9.6 多脚本管线一致性检查

当论文使用≥2个Python脚本生成图表时，L0.5审计必须增加此检查：

```bash
# Step 1: 列出所有生成图表的脚本
grep -l "savefig\|plt.savefig" 03-code/*.py 2>/dev/null

# Step 2: 对每个脚本检查拟合函数实现
# 危险信号：同名函数被重复定义（Python用最后定义的那个）
grep -n "def fit_logspiral\|def fit(" 03-code/*.py

# Step 3: 对每个脚本检查数据路径
grep -n "DATA_DIR\|data_dir\|os.path.*data" 03-code/*.py | grep -v "__pycache__\|#"

# Step 4: 运行各脚本，比较输出数值
# 同一标本/同一管道的拟合RMSE和b必须一致
for script in gen_all_figures.py regenerate_all.py; do
  python3 03-code/$script 2>&1 | grep -E "AC bony|PC bony|LC bony|RMSE|b="
done
```

**SCC实战：4脚本管线一致性检测结果**

| 脚本 | 数据源 | 路径方法 | 输出路径 | RMSE一致? |
|:-----|:-------|:---------|:---------|:---------:|
| `fit_logspiral.py`（修复后） | `/home/yakeworld/scc_fitting` | ✅ nn_path | stdout+figures/ | ✅ 基准 |
| `gen_all_figures.py`（修复前） | `/tmp/inner_ear_canal` | ❌ `argsort` | `figures/` | ❌ AC bony 2.27mm |
| `gen_all_figures.py`（修复后） | `/tmp/inner_ear_canal` | ✅ nn_path | `05-figures/` | ✅ 0.13mm |
| `gen_composite_figure.py` | `/tmp/inner_ear_canal` | ✅ nn_path | `05-figures/` | ✅ |
| `gen_model_comparison.py` | `03-code/data/sp1_microct` | ✅ nn_path | `05-figures/` | ✅ |

### 9.7 Data-to-Figure逐图溯源链

每张图必须可追溯完整链：**原始数据(.mrk.json/.csv) → 拟合脚本 → 作图脚本 → 输出PDF**

| 图 | 原始数据 | 拟合 | 作图脚本 | 输出 | 
|:---|:---------|:-----|:---------|:-----|
| Fig 1 | `03-code/data/sp1_microct/*.mrk.json` | `gen_model_comparison.py` 内联 | `gen_model_comparison.py` | `05-figures/model_comparison.pdf` |
| Fig 2 | `04-data/batch_logspiral_params_*.csv` | `gen_uct_vs_ct_fig.py` | `gen_uct_vs_ct_fig.py` | `05-figures/uct_vs_ct_b.pdf` |
| Fig 3 | `/tmp/inner_ear_canal/*/` | `gen_composite_figure.py` 内联 | `gen_composite_figure.py` | `05-figures/centerline_all_specimens.pdf` |
| Fig 4 | Panel A: `03-code/data/sp1_microct/{pc,lc}.mrk.json`; Panel C: CSV | `gen_fig4_full.py` 内联 | `gen_fig4_full.py` | `05-figures/scc_cochlea_comparison.pdf` |
| Fig S1-S3 | `/tmp/inner_ear_canal/{micro_ct,MRN,industrial_CT}/` | `gen_all_figures.py` 内联 | `gen_all_figures.py` | `05-figures/centerline_3d_fits_sp{1,2,3}.pdf` |

**审计要点**：对每张图确认：数据文件存在、生成脚本存在且可执行、脚本路径正确、输出PDF标签正确、不同脚本对同一标本结果一致。

### 9.8 数据质量检查报告模板

每次L0.5审计产出 `07-quality/data-quality-audit-report.md`：

```markdown
# SCC论文数据质量检查报告
## 检查日期：{date}

## 1. 原始数据来源检查
| 数据集 | 源文件 | 验证 |

## 2. 数据采集代码和原理
| 组件 | 代码 | 验证 |

## 3. 作图代码验证
| 图 | 文件名 | 生成脚本 | 数据源 | 映射完整? |

## 4. 发现的问题与修复
| # | 问题 | 严重度 | 状态 | 说明 |

## 5. 结论
- ✅ 无虚构数据 / ✅ 无虚假图表 / 🟡 待确认
```
