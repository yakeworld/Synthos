# 论文产出合并与目录整理工作流

> 用途: 当 Synthos 生成大量论文（50+篇）后，统一合并到 `outputs/papers/`
> 2026-05-22 session: 50篇散落→12篇顶层+33篇综述6主题目录

## 触发条件

- `outputs/papers/` 中有 >30 个目录
- 出现 -lit / -r2 / 无后缀三副本
- 同一主题出现在 >3 个不同位置
- 用户要求"合并"或"整理"

## 步骤

### Step 0: 外部来源扫描（跨目录归并时先做）

论文可能分散在多个位置，不只有 `outputs/papers/` 内部。先扫描所有可能位置：

```bash
# 常见外部位置
LOCATIONS=(
  "/media/yakeworld/sda2/academic_writer/"
  "/home/yakeworld/桌面/article_todo/"
  "/media/yakeworld/sda2/投稿文件汇总/"
  "/home/yakeworld/paper-improvement/"
  "/home/yakeworld/Synthos/outputs/papers/"
)

for loc in "${LOCATIONS[@]}"; do
  [ -d "$loc" ] && echo "✓ $loc ($(find "$loc" -name '*.tex' 2>/dev/null | wc -l) tex, $(find "$loc" -name '*.pdf' 2>/dev/null | wc -l) pdf)"
done
```

对每个位置判断内容归属（与 `outputs/papers/` 已有目录对比）：

| 判定 | 操作 |
|:-----|:------|
| 已有目录且同主题 | **cp 合并**内容到已有目录（保留原位置不动） |
| 新主题论文 | mkdir + **cp**，如 `3d-sobel-edge-detection/` |
| 待定归属 | 归入 `_todo/`，待后续分类 |
| 非论文文档 | 归入 `_docs/`（修改说明、测试计划、投稿表单等） |

**铁律：第一次操作全用 cp（复制而非移动），原始位置保留不动。** 确认归并无误后再手动删除原始文件。大目录（含 notebook/大图）用 cp -r 可能超时，分批复制。

### Step 1: 内部全面扫描（仅 output/papers/ 内部）

```bash
cd <synthos_root>/outputs/papers

# 列出所有论文
for d in */; do
  tex=$(ls "$d/"*.tex 2>/dev/null | head -1)
  echo "$(wc -c < "$tex" 2>/dev/null | tr -d ' ') $d ($(wc -l < "$tex" 2>/dev/null)行)"
done | sort -rn
```

### Step 2: 检测重复

### Step 2.5: 版本去重（同一论文多版本）

当同一论文从不同来源（如 `academic_writer/` 和 `Synthos/outputs/papers/`）出现多版本时：
1. 对比标题确认是否同一论文
2. 对比行数/文件大小判断哪个更完整
3. 用版本后缀区分，**不删除任何版本**（保留原始文件不动）：
   ```
   paper-synthos-v1.tex        # Synthos管线产出版
   paper-academic-writer.tex    # academic_writer版（通常更长）
   todo-version/                # 桌面待处理版（通常含完整图片）
   ```
4. 写 VERSION 注释或重命名操作记录在 MERGE_LOG.md

**版本命名规范**：`{paper-topic}-{source-name}-v{number}.tex`
- source-name: `synthos`、`academic-writer`、`todo`、`submission`
- 不删除旧版，保留全部版本供后续对比

### Step 3: 分类

| 类型 | 判断标准 | 操作 |
|:-----|:---------|:-----|
| **完整论文** | ≥30行，有完整IMRaD结构 | 保留顶层目录 |
| **小综述** | 20-30行，标题含"Literature Review:" | 归入 `lit-reviews/<topic>/` |
| **真重复** | MD5一致，或标题完全相同 | 删除非最新版本 |
| **同主题多版本** | 3篇同标题含-lit/-r2 | 保留最完整版本，删除其余 |
| **放错位置** | 标题与主题域完全不符 | 移走或删除 |

### Step 4: 主题分组

```
lit-reviews/
├── VOR/               # vor-decode, vor-nn, vis-vest-integration
├── eyeball/           # eyeball-seg, eyeball-torsion, dual-ellipse
├── iris/              # eye-iris-biometric, iris-3d-reconstruct
├── eye-tracking/      # portable-et, headmount-et, itrace-kappa, 4d-eye-vector
├── BPPV/              # bppv-3d-sim, bppv-biomech, psc-bppv, otolith
└── methods/           # shape-prior, t3emnet, pinn, video-anomaly, mri-nystagmus
```

### Step 5: 创建索引

在 `outputs/papers/README.md` 中列出所有论文：

```markdown
# Synthos 生成论文索引

> 更新日期: YYYY-MM-DD | 顶层论文: N 篇 | 主题综述: M 类 K 篇

## 📄 顶层论文

| 论文 | 目录 | 行数 | 主题域 |
```

### Step 5.5: 引用PDF归入论文目录

**铁律：参考文献PDF必须存放在对应论文目录下的 `pdfs/` 中，而非父级。** 每次合并后检查：

```bash
# 检查是否有顶部级别的引用目录（应不存在）
ls -d synthos-refs/ 2>/dev/null && echo "⚠️ 需要移入论文目录"

# 检查论文目录是否已有 pdfs/
ls -d synthos-system-paper/pdfs/ 2>/dev/null || echo "❌ 缺失 pdfs/ 目录"

# 移动外部引用到论文目录
mv synthos-refs/* synthos-system-paper/pdfs/
rm -r synthos-refs/
```

**同时清理过期文件：** 旧的独立版本（如 `synthos-paper-v2.tex`）在合并后应当删除，避免混淆。

### Step 6: 建立 NotebookLM 映射

**必做步骤** — 每篇论文必须与其 NotebookLM 项目关联，否则无法执行 Q1-Q5 质量门。

创建 `papers-to-notebooks.md`：

每行格式：
```
| 论文目录 | NotebookLM 项目名 | 项目ID(前8位) | 状态 |
```

```bash
# 映射模板
notebooklm list | grep -i "partial_paper_title"
# 如果有匹配 → 记录ID
# 如果无匹配 → notebooklm create "完整论文标题"
```

### Step 7: 创建合并日志

每次跨目录归并后，在 `outputs/papers/MERGE_LOG.md` 记录：

```markdown
# 论文归并日志

> 日期: YYYY-MM-DD

## ① 重叠合并（内容合并到已有目录）
| 来源 | 目标 | 操作 |

## ② 新论文归集（从其他位置迁入的新目录）
| 来源 | 目标目录 |

## ③ 非论文文档归集
| 来源 | 目标 |

## ④ 待定事项
- 需后续确认归属的论文
```

记录后，用户可据此验证归并正确性。

## 已知陷阱

| 陷阱 | 避免 |
|:-----|:------|
| 误删唯一副本 | 删除前先 `diff` 确认内容完全相同 |
| -lit 和 -r2 未必是同一论文 | 需验证标题是否相同，有时是不同主题的独立综述 |
| .Trash-1000 文件可能需先恢复 | 使用 `cp` 而非 `mv`，验证后再删除源 |
| notebooklm source add 大文件失败 | 改用 note create 保存 |
| **易遗漏的外部位置** | 除 `academic_writer/` 外，检查 `桌面/article_todo/`、`投稿文件汇总/`、`~/paper-improvement/`、`~/Synthos/` |
| **大目录 cp -r 超时** | 含 notebook/图的目录分批复制，不要一次性全部 cp -r |
| **桌面路径含控制字符** | `桌面/article_todo/` 子目录名含 `\r` 换行，ls 输出用 `-b` 看原始字符 |
| **int 或非论文文档混入** | article2(文献质量评估)/article3(测试计划)/article4(修改说明)不是论文，归入 `_docs/`
