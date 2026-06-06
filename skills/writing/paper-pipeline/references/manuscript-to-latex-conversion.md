# 手稿→LaTeX 直接转换流程

> 当已有完整 Markdown 手稿时，绕过 P1-P2，直接进入 P3 编译。
> 2026-06-05 实战：5篇 BPPV 手稿（共 2,787 行）→ 5篇 LaTeX 论文，平均 20p/篇。

## 适用条件

| 条件 | 判定 |
|:-----|:------|
| 有完整结构的 Markdown 手稿 | ✅ 直接转换 |
| 含 Abstract/Introduction/Methods/Results/Discussion | ✅ 保留结构 |
| 引用标记为 [^xx] 格式 | 需转化为 \cite{xx} |
| 中英文混杂 | 过滤中文注释，保留科学内容 |

## 转换流程

```
手稿评估 → 确定是否已入库 → 创建目录 → delegate_task写LaTeX → 编译验证 → 注册tracker
```

### Step 1: 手稿评估
```bash
# 统计行数和结构
wc -l manuscript.md
grep "^## " manuscript.md  # 提取所有section标题

# 检查是否已入库
grep "paper-name" Synthos/outputs/papers/agent-tracker.json
```

### Step 2: delegate_task 模板
```python
delegate_task(
  context=f"手稿路径: {path}\n作者: ...\n目标期刊: J Vestibular Res\n格式: elsarticle",
  goal="""读取手稿全文→创建 paper.tex (elsarticle, ≥25篇refs)
          →创建 paper.bib→编译 pdflatex→bibtex→pdflatex→pdflatex
          →确认0错误→记录PDF页数和大小"""
)
```

### Step 3: 合并策略
当同一主题有多个版本手稿时：
- 以结构化版本为主框架
- 融合综合版本的临床讨论内容
- 输出合并后的统一LaTeX

### Step 4: 注册
- agent-tracker.json: completed_papers + notes
- paper-inventory.md: 更新状态

## 陷阱
- [^xx] 引用标记→\\cite{xx} 可能漏转换 → 编译检查 undefined refs
- 手稿中英文混杂 → 中文背景注释需过滤（LaTeX默认不支持CJK字符）
- 大文件(>800行) → 先提取结构再委托
- `elsarticle` vs `article` 模板 → 始终用 elsarticle（团队标准）
- **step_gap_analysis.md 可被覆盖**: NotebookLM或orchestrator重新扫描时，可能用摘要替换原始的D1-D10a结构分析。在gap分析写入paper步骤前，确认step_gap_analysis.md保持完整D1-D10a结构。如果已被替换（文件变小、结构消失），从agent-tracker.json的notes字段重建。
- **中文哲学引用导致LaTeX编译失败**: Synthos哲学引用（如"文以验法"）在paper.tex中会触发LaTeX Unicode错误。编译前搜索CJK字符并替换为英文等效表达。
