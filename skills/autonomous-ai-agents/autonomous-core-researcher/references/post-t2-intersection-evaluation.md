# Post-T2 交集空白评价矩阵

> 当所有5个核心方向≥T2时, 进入交集空白分析。本文件提供候选交集优选的实战模板和评分框架。

## 实战模板 (2026-05-25 验证)

### Step 1: 枚举 C(5,2) = 10 个交集对

用格点矩阵快速评估每个交集的候选质量:

```
                     Core1    Core2    Core3    Core4    Core5
                     (3D眼动)  (Kappa角) (VOR)   (BPPV)   (PD)
Core1 (3D眼动)         —       ✅已有    ⚠️部分   ✅已有   ✅已完成
Core2 (Kappa角)                —       ⚠️部分   ❌弱     ❌弱
Core3 (VOR)                           —       🔥强潜力  🔥强潜力
Core4 (BPPV)                                     —       🔥中等
Core5 (PD)                                               —
```

**判定标准**:
- ✅ 已有: 该方向已有现成论文覆盖
- ⚠️ 部分: 有交叉但未以该交集为主要焦点
- ❌ 弱: 两个方向的实际交叉缺少研究证据
- 🔥 强潜力: 有明确临床/技术交叉, 无现有论文覆盖, 可写综述

### Step 2: 评分每个候选交集 (0-5分)

| 候选交集 | 研究证据量 | 综述可行性 | 临床/技术意义 | 连接已有论文 | 总分 |
|:---------|:----------:|:----------:|:------------:|:-----------:|:----:|
| Core3(VOR)∩Core4(BPPV) | 4 | 5 | 5 | 4 | **18** |
| Core3(VOR)∩Core5(PD) | 3 | 4 | 4 | 3 | **14** |
| Core4(BPPV)∩Core5(PD) | 2 | 3 | 3 | 3 | **11** |
| Core1(3D眼动)∩Core2(Kappa角) | 3 | 2 | 3 | 3 | **11** |

**评分细则**:
- **研究证据量**(0-5): 文献中有多少篇直接讨论两个方向的交叉? 用 OpenAlex 搜索 `方向A AND 方向B` 快速评估
- **综述可行性**(0-5): 能否纯文本完成(综述/系统综述=5)? 是否需要实验(方法论文=1-3)?
- **临床/技术意义**(0-5): 该交集解决的是真问题还只是学术填充? 临床入口越大分越高
- **连接已有论文**(0-5): 能否直接引用两个方向下已有的论文作为Material/Background?

### Step 3: 快速验证

对总分>12的候选, 执行快速验证:

```bash
# 1. OpenAlex 验证研究证据量
curl -s "https://api.openalex.org/works?filter=title_and_abstract.search:<方向A>%20<方向B>&sort=cited_by_count:desc&per_page=5" -o /tmp/verify.json
python3 -c "
import json
with open('/tmp/verify.json') as f:
    data = json.load(f)
print(f'Total results: {data.get(\"meta\",{}).get(\"count\",0)}')
for w in data.get('results',[])[:3]:
    print(f'  [{w.get(\"publication_year\")}] {w.get(\"title\",\"\")[:80]}')
"

# 2. 检查 NotebookLM 项目
notebooklm list 2>/dev/null | grep -i "<关键词A>|<关键词B>"

# 3. 检查现有论文目录是否有交叉
ls /media/yakeworld/sda2/Synthos/outputs/papers/*/paper.tex 2>/dev/null | xargs grep -l "<方向A>" 2>/dev/null
ls /media/yakeworld/sda2/Synthos/outputs/papers/*/paper.tex 2>/dev/null | xargs grep -l "<方向B>" 2>/dev/null
```

### Step 4: 最终决策

按照以下优先级选择:

```
1. 有 NotebookLM 项目的可选 → 最快启动
2. 综述 > 方法论文 (无需实验)
3. 连接两个方向的综述 > 全新主题
4. 总分更高的优先
```

## 已知候选优先级 (2026-05-25 状态)

| 优先级 | 交集 | 论文方向 | 可行性 |
|:------:|:-----|:---------|:------:|
| 🔴 P0 | Core3(VOR)∩Core4(BPPV) | VOR Assessment in BPPV Diagnosis | 系统综述, vHIT用于BPPV鉴别诊断, 已有VOR和BPPV两方向论文做Material |
| 🟡 P1 | Core3(VOR)∩Core5(PD) | VOR Abnormalities in Parkinson's Disease | 系统综述, VOR gain/suppression变化在PD中有文献, 需要多搜索验证 |
| 🟢 P2 | Core1(3D眼动)∩Core2(Kappa角) | Kappa角对3D眼动追踪精度的影响 | 工程/方法论文, 可能需要实验验证 |
| 🟢 P2 | Core4(BPPV)∩Core5(PD) | BPPV Prevalence in Parkinson's Disease | 临床关联综述, 文献量可能有限 |

## 降级兜底: 无交集可选时

当10个交集对评估均无高分(总分≤10), 或所有P0候选已被用尽时:

1. 进入 **hold 论文再评估**: 检查三个 hold 论文的条件是否变化
2. **T1 提升模式**: 选择已有论文中评分最低但还有提升空间的, 从T2补到T1
3. **扩展方向边界**: 如果5个核心方向均已饱和, 记录到 agent-tracker 并返回 [SILENT]
