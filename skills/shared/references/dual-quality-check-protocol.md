# 双质量检查协议（Dual Quality Check Protocol）

> 核心理念：**凡稿必双检，内审外审皆过乃可投。**
> 凝练自 2026-05-23 Synthos 论文三轮评审实践。

## 架构

```
论文完成
    ↓
G1-G7 管线闸门（过程正确性）
    ↓
┌─────────────────────────────────────┐
│        双质量检查（并行执行）         │
│                                     │
│  Layer A: 本地评审（内部系统）       │
│  ┌─────────────────────────────┐    │
│  │ ① L0 动灵评估              │    │
│  │ ② L0.5 数据诚实门          │    │
│  │ ③ 7维SCI评审+证据引用      │    │
│  │ ④ 期刊感知阈值判定         │    │
│  └─────────────────────────────┘    │
│                                     │
│  Layer B: 外部评审（NotebookLM）    │
│  ┌─────────────────────────────┐    │
│  │ ① 上传论文到NotebookLM      │    │
│  │ ② Gemini 7维SCI评审         │    │
│  │ ③ 【必答】补救方案提取       │    │
│  │ ④ 评分校准(−0.05~−0.15)      │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
    ↓
差距分析（取两方最低分）
    ↓
修订循环（一次一维）
    ↓
双质检 avg ≥ 阈值？
    ├── ✅ → 论文可投
    └── ❌ → 继续修订
```

## Layer A: 本地评审（内部系统）

### Step A1: L0 动灵评估（系统描述论文专用）
[同前—五维度：方向性/生化度/生长性/原生感/自律性]

### Step A1.5: 数据诚实门（L0.5）— 凡数必源，不源不取

**核心理念**：LLM可以评估"论证好不好"，但LLM无法评估"论证真不真"——真/假需要外部世界对齐。论文写得像真的 ≠ 数据是真的。

**执行流程**：

```bash
# 1. 提取论文中所有数值声明
grep -n '%' paper.tex > /tmp/declarations.txt
# 2. 对每条声明追溯源文件：
#    evolution数据 → evolution-state.json / evolution-log.md
#    benchmark数据 → BENCHMARKS.md / golden test logs
#    吸收记录 → absorption-tracked.json
#    实验结果 → 实验日志/代码输出
# 3. 逐条判定：
#    ✅ 有源文件且一致 → 保留
#    🟡 理论推算 → 标注 "estimated"
#    ❌ 无源文件 → 删除
# 4. 全部通过（✅或🟡）→ 进入 Step A2
```

**2026-05-23 实战教训**：Synthos论文中N=50外部定量对比表在本地和Gemini评审中均获高分(0.95+)，但该数据从未被实验执行过——是LLM生成的虚构数据。根因：评审专注于"论文写得好不好"而跳过了"数据真不真"。

### Step A2: 7维SCI评审

```bash
cd <submission_dir>/
echo "总字符数:" && wc -m paper.tex
echo "table数:" && grep -c 'begin{table}' paper.tex
echo "figure数:" && grep -c 'begin{figure}' paper.tex
echo "cite次数:" && grep -o 'cite{' paper.tex | wc -l
echo "bibitem数:" && grep -c 'bibitem' paper.tex
echo "自引率:" && grep -oP '\\cite\{([^}]+)\}' paper.tex | \
  sed 's/\\cite{//;s/}//' | tr ',' '\n' | sort -u | \
  awk '{if(/yang/) s++; t++} END{printf "%d/%d=%.1f%%\n",s,t,s/t*100}'
```

| 指标 | 通过条件 |
|:-----|:---------|
| 总字符数 | >20,000 |
| table数 | ≥2 |
| cite次数 | ≥30 |
| bibitem数 | ≥30 |
| 自引率 | <15% |
| pdflatex编译 | 零错误 |

### Step A2: L0 动灵评估（系统描述论文专用）

仅当论文描述系统/架构/框架时执行。按五维度评分：

| 维度 | 问句 | 1-5分 |
|:-----|:-----|:------|
| 方向性 | 哲学根基是否驱动设计？ | 1=纯操作手册, 5=哲学是基因 |
| 生化度 | 外部概念是否被完全转化？ | 1=原样搬运, 5=完全消化 |
| 生长性 | 数据是否反映最新状态？ | 1=严重过时, 5=完全同步 |
| 原生感 | 读起来是自发生长的？ | 1=显然搬来, 5=浑然一体 |
| 自律性 | 论文是否完整自洽？ | 1=强依赖, 5=自洽闭环 |

**判定**：平均 ≥4.0 → 进入7维评审；<4.0 → 先修复动灵最低维。

### Step A3: 7维SCI评审

按 sci-paper-quality-review 标准执行，反模拟铁律（凡评必核）。

### Step A4: 期刊感知阈值判定

| 层级 | avg阈值 | 单维最低 | 引用数要求 |
|:-----|:-------:|:--------:|:----------:|
| T1 (Nature MI/Patterns) | ≥0.85 | ≥0.70 | ≥60 |
| T2 (JAIR/Intelligent Computing) | ≥0.80 | ≥0.60 | ≥40 |
| T3 (IEEE Access/Frontiers) | ≥0.75 | ≥0.50 | ≥30 |
| T4 (Workshops) | ≥0.70 | ≥0.50 | ≥20 |

## Layer B: 外部评审（NotebookLM/Gemini）

### Step B1: 上传论文

```bash
# 先清理旧版本
# 用Python客户端删除旧论文source(s)
# 用note create上传新版本（source add失败时的降级通路）
notebooklm use <project_id>
notebooklm note create "$(cat paper.tex)" --title "Paper v<N>"
```

### Step B2: Gemini 7维SCI评审

```bash
notebooklm use <project_id> && notebooklm clear
notebooklm use <project_id>
notebooklm ask "对论文进行7维SCI质量评审。每维评分0-1.0并给出改进建议。"
```

### Step B3: 补救方案提取

当Gemini评分<0.85时，要求【必答】补救指令：

```
**【必答】对于评分<0.85的维度，请逐一给出具体补救方案：**
- 缺失了什么？列出标题/DOI
- 应该用什么检索词在哪个数据库搜索？
```

### Step B4: 评分校准

NotebookLM评分通常偏高+0.05~+0.15，视为上限分数。本地评审作为下限分数。

```
校准后评分 = (本地评分 + Gemini评分) / 2
```

## 双质检差距分析

| 条件 | 行动 |
|:-----|:------|
| 两方avg均≥阈值 | ✅ 论文可投 |
| 一方通过一方不通过 | 🟡 取最低分进入修订 |
| 两方均不通过 | 🔴 找最低共同维度修复 |

## 修订循环

一次一维，从双质检共同最低分开始。

```bash
1. 找双质检共同最低分维度
2. 执行修复（改.tex文件）
3. pdflatex编译验证
4. 重新上传NotebookLM
5. 重跑双质检
6. 达标 → ✅ 完成；不达标 → 继续下一维
```

## 与 quality-gate 的关系

```
quality-gate L3 管线级 (G1-G7) → 过程正确性
    ↓
quality-gate L4 内容级 (SCI评审) → 触发双质量检查
    ↓
双质量检查 → 本地评审(Layer A) + Gemini评审(Layer B)
    ↓
汇总判定 → 论文可投或继续修订
```
