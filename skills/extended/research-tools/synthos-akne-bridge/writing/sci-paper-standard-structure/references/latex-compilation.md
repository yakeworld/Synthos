# LaTeX Compilation Guide

> pdflatex 单次编译不生成参考文献。必须运行完整链。

## 完整编译流程

```bash
# 1. 第一次 pdflatex — 生成 .aux（含引用标签）
pdflatex -interaction=nonstopmode paper.tex

# 2. bibtex — 从 .bib 读取参考文献，生成 .bbl
bibtex paper

# 3. 第二次 pdflatex — 解析参考文献引用
pdflatex -interaction=nonstopmode paper.tex

# 4. 第三次 pdflatex — 最终解析所有交叉引用
pdflatex -interaction=nonstopmode paper.tex
```

单条命令链：
```bash
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

## 常见问题

### 参考文献不显示
- 原因：只跑了 pdflatex 一次，没跑 bibtex
- 修复：运行完整 4 步链
- 验证：`grep -c "citation" paper.aux` — 应该 > 0

### `\bibdata` 或 `\bibstyle` 未找到
- 原因：paper.tex 中的 `\bibliography{references}` 或 `\bibliographystyle{plainnat}` 命令损坏
- 常见：Python f-string 中 `\b` 被解析为退格符 → `\bibliography` 变成 `^Hibliography`
- 检查：`cat -A paper.tex | tail` — 看 `\b` 是否正常
- 修复：在 Python 中避免 `r"""..."""` 中出现 `\b`，或手动替换
  ```python
  content = content.replace('\x08ibliographystyle', '\\bibliographystyle')
  content = content.replace('\x08ibliography', '\\bibliography')
  ```

### empty journal 警告
- 原因：BibTeX 条目缺少 journal 字段
- 影响：无（arXiv 论文默认无 journal）
- 修复：加 `journal = {arXiv preprint}` 可消除警告

### Undefined citation warnings
- 原因：bibtex 还没跑，或 .bib 中没有该 citation key
- 修复：先跑 bibtex，然后 pdflatex 两次
- 检查：`bibtex paper 2>&1 | grep warning` 查看具体缺失键

## 验证

- [ ] `grep -c "citation" paper.aux` ≥ 论文中引用数
- [ ] `bibtex paper 2>&1 | grep -i error` 无错误
- [ ] `pdfinfo paper.pdf | grep Pages` ≥ 5
- [ ] PDF 末尾有 References 章节
