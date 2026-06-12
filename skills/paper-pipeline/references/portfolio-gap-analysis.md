# Portfolio Gap Analysis — 从研究组合中发现新论文主题

> 2026-05-25 | 衍生于11篇已完成论文的扫描，发现DR-AI交叉空白并创建新论文

## 核心理念

当研究组合（portfolio）积累到一定规模（≥5篇完成论文），不应随机选择下一个主题。应**系统性扫描已完成论文的主题覆盖**，识别"白色空间"（white space）——即实验室已有专长但尚未被整合覆盖的研究维度。

## 五步流程

### Step 1: 扫描目录 → 主题聚类

从完成的论文列表中提取每个论文的核心主题域：

```python
# 伪代码
papers = [
  ("bppv-minimal-stimulus", "前庭/BPPV"),
  ("vor-digital-twin", "前庭/VOR"),
  ("pd-torsion-review", "帕金森/眼科学"),
  ("pima-crispdm", "糖尿病/机器学习"),
  ("synthos-system-paper", "AI系统/认知架构"),
  ("iris-yolo", "虹膜/计算机视觉"),
  ("iris-3d-anatomical-opt", "虹膜/3D建模"),
  ("hcs3wt-breast-cancer", "乳腺癌/三分类AI"),
  ("vor-sparse-modular", "前庭/VOR/数字孪生"),
  ("pd-dysphagia-2026", "帕金森/吞咽"),
  ("vog-vestibular-review", "前庭/VOG/系统综述"),
]
```

### Step 2: 构建主题领域地图

按顶层域归组，识别覆盖密度：

| 主题域 | 论文数 | 覆盖度 | 覆盖的维度 |
|:-------|:------:|:------:|:-----------|
| 前庭/VOR/BPPV | 4 | 🔴 密集 | 数字孪生, 稀疏模块, 最小刺激, VOG综述 |
| 帕金森病 | 2 | 🟡 中等 | 眼动扭转, 吞咽障碍 |
| 虹膜/眼球成像 | 3 | 🟡 中等 | YOLO检测, 3D解剖, 3D重建 |
| 医疗AI/临床ML | 3 | 🟡 中等 | 乳腺癌3WT, 糖尿病PIMA, Synthos系统 |
| **视网膜疾病** | **0** | **⚪ 空白** | **无论文覆盖** |
| 角膜疾病 | 0 | ⚪ 空白 | — |
| 青光眼 | 0 | ⚪ 空白 | — |

### Step 3: 定位最自然拓展方向

选择标准：
- **连接已有专长**（最好跨2+已覆盖域）
- **临床价值高**（全球疾病负担大）
- **可实现**（无需新实验，系统综述即可）
- **文献充足**（有足够已发表的文献支撑）

评分矩阵示例：

| 候选主题 | 连接已有专长 | 临床价值 | 可实现性 | 文献充足 | 总分 |
|:---------|:-----------:|:--------:|:--------:|:--------:|:----:|
| **DR-AI筛检** | 糖尿病+眼部影像 | 5/5 | 5/5(综述) | 5/5 | **20** |
| 青光眼AI诊断 | 眼部影像 | 5/5 | 4/5(综述) | 4/5 | 18 |
| AMD深度学习 | 眼部影像 | 4/5 | 4/5(综述) | 4/5 | 16 |
| 圆锥角膜检测 | 虹膜/眼球 | 3/5 | 3/5(综述) | 3/5 | 12 |

### Step 4: 快速文献验证

确认候选主题有足够的已发表文献支撑论文写作：

```bash
# arXiv查AI/CS方向
curl -s "https://export.arxiv.org/api/query?search_query=all:TOPIC+A+AND+TOPIC+B&max_results=5" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
print(f'Total hits: {len(root.findall(\"a:entry\", ns))}')
for e in root.findall('a:entry', ns)[:3]:
    print(f'  - {e.find(\"a:title\", ns).text.strip()[:80]}')
"

# OpenAlex查引用数据（串行，防429）
python3 -c "
import json, urllib.request, time
url = f'https://api.openalex.org/works?search={urllib.parse.quote(QUERY)}&sort=cited_by_count:desc&per_page=5&filter=publication_year:2020-2026'
# ... (see research-paper-search skill for full pattern)
"
```

**验证通过条件**：至少找到10+篇高引用（>50 cites）核心文献 + 5+篇2024-2026时效文献。

### Step 5: 形式化假设 → 创建论文

**不写全篇，先写框架。** 一个系统综述的初始假设结构：

```
H₁（主假设）：[新维度]的系统性整合揭示[已有领域]中未被认知的规律
  → 可证伪条件：if 已有N篇高质研究使用了该维度却无新发现，则H₁被证伪
H₂（冗余假说）：[新维度]与[已有维度]高度相关(r>0.9)，信息冗余
H₃（噪声假说）：[新维度]的贡献被过度声明，实际增量有限
```

创建目录和初始草稿：
```bash
mkdir -p outputs/papers/{paper-name}/{sections,figures}
# paper.tex: 40-50行框架 → 逐步充实
```

## 陷阱

1. **❌ 随机选主题**：不扫描已完成组合直接拍脑袋选主题，导致重复或边缘领域。**先扫描再决策，看白色空间在哪**。
2. **❌ 单一维度判断**：只看"没人做过"忽略"做它的意义"。用评分矩阵综合评估。
3. **❌ 跳过文献验证**：选好主题后不确认文献存量就直接写，写到半路发现没引文支撑。先搜后写。
4. **⚠️ 遗忘scf-paper类untracked资产**：目录根部的独立.tex文件可能代表进行了50%的未完成工作。扫描时检查所有.tex文件位置，而不仅限于子目录。

## 实战案例

**2026-05-25:** 11篇完成论文覆盖前庭/VOR(4)、帕金森(2)、虹膜(3)、医疗AI(3)。白色空间=视网膜疾病+AI。DR-AI筛检直接连接糖尿病(pima-crispdm)和眼部影像(iris-yolo, iris-3d)双重专长。arXiv检索确认文献充足→创建dr-ai-screening系统综述v1，33引用，10页。
