# Synthos + NotebookLM 论文润色改进工作流

> paper-pipeline P4质量门的操作手册
> 定义如何使用NotebookLM闭环优化论文

---

## 核心循环

```
paper.tex ─→ NotebookLM(外部审稿人) ─→ 7维Q&A评分 + 改进建议
    ↑                                           ↓
    │                                     分类处理(P0-P3)
    │                                           ↓
    └── 重编译 ← 本地修改 ←─ 自动执行/用户确认
```

## 操作步骤

### Step 1: 上传论文到NotebookLM

```bash
# 从 papers-to-notebooks.md 查项目ID
grep "论文名" outputs/papers/papers-to-notebooks.md

# 切到对应项目
notebooklm use <project_id>

# 上传最新源码（两种方式均可）
cat paper.tex | notebooklm note create "Paper v<N> - <title>"
# 或
notebooklm source add paper.md
```

### Step 2: 7维Q&A评审

```bash
notebooklm ask "请对论文进行全面7维SCI质量评审..."
```

### Step 3: 提取建议并分类

读取NotebookLM回答，按优先级分类：

| 优先级 | 判定 | 行动 |
|:------|:-----|:-----|
| P0 🔴 | D7引用安全风险/D2数学错误 | 立即修复 |
| P1 🟡 | 评分<0.85的维度 | 进入修订循环 |
| P2 🟢 | 评分≥0.85但有小优化 | 可选优化 |
| P3 ⚪ | 新内容建议(新图/表/实验) | 记录待办 |

### Step 4: 执行修订

置信度≥80%的改进自动执行；<80%展示给用户确认。

修改后重编译：
```bash
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

### Step 5: 递归循环

```
v3 → 上传 → 评审(0.95) → 改进 → v3.1 → 重新上传 → 再评审 → 评分达标? → 完成
                                                              ↓ 未达标
                                                         继续修订
```

## 评审记录保存

每次评审结果保存到两处：
1. `outputs/papers/papers-to-notebooks.md` → 质量评审记录节（评分摘要）
2. `<paper-dir>/notebooklm-review.md` → 完整详细建议

## 已知陷阱

1. **长TeX文件超时** — >1000行的.tex可能超时。拆分上传
2. **评审对话积累** — 多轮Q&A后超时。每1-2轮 clear 重建对话
3. **评分偏差** — NotebookLM评分偏高+0.05~0.15
4. **大文件上传** — 改用 `notebooklm source add` 而非 `note create`
