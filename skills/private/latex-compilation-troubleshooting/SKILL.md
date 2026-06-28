---
name: latex-compilation-troubleshooting
description: "LaTeX编译问题排查与修复全流程 — 从错误诊断到干净编译。覆盖Unicode、包兼容性、路径、环境嵌套、bib等。"
version: 1.1.0
author: "Synthos + 杨晓凯"
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: troubleshooting
    description: "LaTeX编译问题排查与修复全流程"
    signature: "error_message: str -> root_cause: str; root_cause -> fix_plan: list"
    related_skills: [paper-pipeline, paper-repair, sci-paper-quality-review]
---

# LaTeX Compilation Troubleshooting

> 编译错误→根因定位→针对性修复→验证编译。

## 执行流程

### 1. 首次编译
```bash
cd /path/to/paper
rm -f paper.aux paper.log paper.out paper.spl paper.blg paper.bbl paper.pdf
pdflatex -interaction=nonstopmode paper.tex 2>&1 | grep '! LaTeX Error'
grep -c 'undefined' paper.log
```

### 2. 错误分类与修复

#### A. LaTeX Errors (致命)

**Paragraph ended before \\@sect was complete + Too many }'s** 🔴 NEW 2026-06-16 — Orphan/auto-assembled papers
- **根因**: `\subsection{Title` 或 `\section{Title}` 缺少闭合 `}`。LaTeX将段落中第一个 `}` 作为该节的闭合括号，导致后续全部大括号错位。
- **Detection**: `grep -nP '\\\\\\\\subsection\{[^}]*$' paper.tex` — 查找行末无 `}` 的 subsection。`grep -nP '\\\\\\\\section\{[^}]*$' paper.tex` — 同理检查 section。也会在 log 中表现为 "Paragraph ended before \\@sect was complete" 紧随 "Too many }'s"。
- **Fix**: 在每行末尾添加 `}`。注意该行后第一个 `}` 已被消耗 — 需删除那个多余的 `}`。例如：
  - 原文：`\subsection{Quality Assessment\n\n\subsubsection{PRISMA Checklist}\n...).}` → 改为：`\subsection{Quality Assessment}\n\n\subsubsection{PRISMA Checklist}\n...).`
- **已验证**: vor-bppv-diagnosis, 27pp elsarticle systematic review, 两处 `\subsection{Quality Assessment` 均缺少 `}`。

**Stray \\end{figure} orphan — `\\begin{document} ended by \\end{figure}`** 🔴 NEW 2026-06-16
- **根因**: 模板或自动组装遗留的多余 `\end{figure}`，位于 `\end{table}` 和另一个 `\begin{figure}` 之间。无对应 `\begin{figure}`。
- **Detection**: 对比 `\begin{figure}` 与 `\end{figure}` 计数：
  ```bash
  grep -cP '\\\\\\\\begin{figure}' paper.tex   # 应等于
  grep -cP '\\\\\\\\end{figure}' paper.tex     # 这个数
  ```
  如果不等 → 多余的是玄关（多一个）或缺失（少一个）。位置通常在 `\end{table}` 附近或两个 figure block 之间。
- **Fix**: 找到多余的 `\end{figure}` 并删除。注意不要删错匹配的 `\end{figure}` — 用 `grep -n` 查看行号确认上下文。
- **已验证**: vor-bppv-diagnosis, line 331, 位于 `\end{table}` (line 330) 和 `\begin{figure}` (line 334) 之间。

**Missing \\begin{document}**
- 根因：preamble中插入内容破坏了`\\begin{document}`位置
- 检查：`\\graphicspath`是否缺少闭合括号 `}}`
- 检查：`\\usepackage`是否插入在`\\begin{document}`之后
- 检查：`\\journal{...}`后紧跟`\\begin{document}`，新包必须插在两者之间

**Something's wrong--perhaps a missing \item**
- 根因：`\item`出现在`enumerate`/`itemize`环境之外
- 常见场景：
  - `\begin{highlights}`环境在elsarticle中未定义（需elsarticle-harvard.sty）→ 改为`\begin{itemize}`
  - `equation*`嵌套在`enumerate`/`itemize`的`\item`内 → LaTeX不允许浮动环境在列表环境中
  - 修复脚本中误删了`\begin{enumerate}`但保留了`\item`
- 检查：所有`\item`前面5行内是否有`\begin{enumerate}`或`\begin{itemize}`

**File `xxx' not found** (图片/图形)
- 根因：graphicspath配置错误或图片不存在
- 检查：`\\graphicspath{{05-figures/}}` — 必须是双花括号闭合`{{}}`
- 检查：`\\includegraphics`引用文件名是否与实际文件名一致（.jpg vs 无扩展名）
- 检查：图片文件是否在graphicspath指定的目录中
- elsarticle模板默认graphicspath为`{{figures/},{pics/}}`，需改为实际目录
- **🔴 2026-06-18 实战：符号链接路径陷阱** — 论文在 `outputs/papers/<name>/01-manuscript/` 时，图片在 `05-figures/`（同层）。从 01-manuscript 到 05-figures 的相对路径是 `../05-figures/`，**不是** `../../05-figures/`。后者指向上一层目录（papers/），会找不到文件。
  - 符号链接创建：`ln -sf ../05-figures/Figure_1.jpg Figure_1.jpg`
  - 如果之前用了 `../../`，删除重建：`rm -f Figure_1.jpg && ln -sf ../05-figures/Figure_1.jpg Figure_1.jpg`
  - 验证：`readlink Figure_1.jpg` 应显示 `../05-figures/Figure_1.jpg`
  - 根因：用户之前从其他路径（如 desktop）创建链接时可能用了错误深度

**Undefined control sequence: \\cite{...}** 🔴 NEW 2026-06-18 — `patch` tool double-escaped `\` 
- **根因**: Hermes 的 `patch` 工具在编辑 `.tex` 文件时，会将 `\cite{xxx}` 双转义为 `\\cite{xxx}`。在 LaTeX 中，`\\` 是换行命令，后面跟的 `cite` 是未定义命令。报错表现为 `! Undefined control sequence. \cite` — 虽然 `\cite` 本身是有效的 LaTeX 命令，但因为变成了 `\\cite`，LaTeX 将其解释为 `\\`（换行）+ `cite`（未定义）。
- **Detection**: 
  ```bash
  grep -nP '\\\\\\\\cite' paper.tex   # 查找双反斜杠 cite
  grep -nP '\\\\\\\\section' paper.tex  # 查找双反斜杠 section
  ```
  注意 `grep` 的输出中每个 `\\` 代表一个实际字符 `\`，所以 `\\\\` 在输出中表示两个实际反斜杠。
- **Fix**: 
  ```bash
  sed -i 's/\\\\\\\\cite/\\\\cite/g; s/\\\\\\\\section/\\\\section/g; s/\\\\\\\\begin/\\\\begin/g; s/\\\\\\\\texttt/\\\\texttt/g' paper.tex
  ```
  然后重新编译验证。**每次使用 `patch` 工具编辑 `.tex` 文件后都必须执行此检查**。
- **已验证**: synthos-system-paper introduction step (2026-06-18), 5 处 `\cite` 被双转义。

**Undefined control sequence: \\degree** 🔴 NEW 2026-06-16 — elsarticle clinical/BPPV papers
- **根因**: `\degree{}` 在标准LaTeX和elsarticle中均未定义。临床仿真/BPPV论文中频繁使用角度符号（`135\degree{}`, `45\degree{}`）描述头部旋转角度。
- **Detection**: `grep -nP '\\\\degree' paper.tex` 返回行数 > 0。pdflatex输出 11 个 `! Undefined control sequence` 错误（每处使用各一个），但PDF仍能生成（角度数字显示为裸数字，无 ° 符号）。
- **Fix A（推荐）**: 在导言区加入 `\newcommand{\degree}{\ensuremath{^\circ}}` — 定义角度命令为数学模式中的上标圆圈。
- **Fix B**: 将全部 `135\degree{}` 替换为 `$135^\circ$`（内联数学模式）。
- **Fix C**: 加载 `\usepackage{gensymb}` 然后直接使用 `\degree`（gensymb 包定义了此命令）。
- **注意**: `\usepackage{textcomp}` 不提供 `\degree`（它提供 `\textdegree`），不要混淆。
- **已验证**: bppv-pc-repositioning-optimization (2026-06-16, elsarticle临床仿真, 11处 `\degree`, Fix A 生效, 0错误编译)。

**Unicode character (U+XXXX)**
- 根因：LaTeX默认不支持非ASCII字符
- 解决：替换所有Unicode符号为LaTeX等价物
  - `≈` → `$\approx$`
  - `→` → `$\rightarrow$`
  - `×` → `$\times$`
  - `–` → `--` (en-dash)
  - `—` → `---` (em-dash)
  - `≤` → `$\leq$`
  - `≥` → `$\geq$`
- 或者在preamble添加：`\usepackage[utf8]{inputenc}`（但某些字体仍不支持）

**Environment algorithmic undefined**
- 根因：`algorithmic`包与elsarticle不兼容或加载失败
- 解决：直接删除algorithmic环境（论文通常不需要），或改用`algorithm2e`包
- 检查：`\usepackage{algorithmic}`在preamble中的位置是否正确

#### B. Natbib/Undefined Citations (警告)

**Package natbib Warning: Citation `xxx' undefined**
- 根因：bibtex未执行或引用缺失
- 修复流程：`pdflatex → bibtex paper → pdflatex → pdflatex`
- 检查：paper.bbl是否生成（0字节=失败）
- 检查：paper.blg是否有"0 warnings"
- 如果仍有未定义：检查.bib文件中bibkey是否在.tex中被`\cite{}`引用

#### C. Reference Errors

**Missing \begin{document} after graphicspath fix**
- 根因：正则替换`{{figures/}},{pics/}}`时括号不匹配，导致LaTeX解析器在preamble中找到未闭合括号
- 修复：`\graphicspath{{05-figures/}}` 确保外层`{}`匹配

### 3. 修复验证

```bash
# 编译测试
rm -f paper.*
pdflatex -interaction=nonstopmode paper.tex 2>&1 | grep '! LaTeX Error'
grep -c 'undefined' paper.log

# 如果0错误且0未定义引用 → 成功
# 如果有错误 → 继续修复并重复
```

### 4. 安全守则（铁律）

**操作前必须备份**：\n```bash\ncp paper.tex paper.tex.bak.{timestamp}\n# 或在修改前创建 .bak 文件\n```\n\n**🔴 绝对禁止 `rm -f paper.*` 通配符删除**：\n- `paper.*` 通配符会匹配 `paper.tex`（因为 `.tex` 以 `.t` 开头，匹配 `*`）→ **已发生 2026-06-15 事故**：一次性删除了完整论文源文件\n- 只能删除已确认生成的辅助文件：`rm -f paper.aux paper.log paper.out paper.blg paper.bbl paper.pdf`\n- 删除前用 `ls paper.*` 确认列表中不含 `paper.tex`
- 任何批量操作（replace/patch）前必须创建 `.bak` 备份

**批量修改后验证**：
- 每次 `replace` 或 `patch` 后，立即检查关键部分是否被正确修改
- 编译测试是最快的验证方式

## 陷阱

**Highlignts环境**: `\\begin{highlights}` 是 elsarticle 的扩展环境，需要 `elsarticle-harvard.sty`。默认安装的 elsarticle 不支持。如果报错 `Missing \\item` 且发现 `highlights`，改为 `\\begin{itemize}`。

**D10a 验证 — .bbl 权威来源**：\n- 对于使用外部 `.bib` + `\\bibliography{}` 的论文，D10a **必须**从 `.bbl` 文件验证，而非从 `.bib` 扫描\n- `.bbl` 包含 bibtex 实际解析出的 bibitem keys，是最权威来源\n- 验证方法：`re.findall(r'\\bibitem\{([^}]*)\}', bbl_content)` → 得到确定的 bibitem 集合\n- 然后用 `grep -oP '\\\\cite{[^}]+}' paper.tex | sort -u` 对比 cite keys\n- 常见陷阱：`\\cite{daugman2001statistical, bowyer2008image}` 在注释行（`%%` 开头）中，bibtex 忽略注释 → D10a 不增加 → 必须将引用移至正文
- **equation* in enumerate**: LaTeX 不允许浮动环境（equation*, figure, table）嵌套在 enumerate/itemize 的 item 中。修复方法：将 equation 移到 enumerate 外面，或使用 `minipage` 包裹。

**enumerate[nosep] error**: `\begin{enumerate}[nosep]` 中的 `nosep` 选项来自 `enumitem` 宏包。elsarticle 等标准文档类不自动加载 `enumitem`。修复：去掉 `[nosep]` 使用默认间距，或在导言区添加 `\usepackage{enumitem}`。

**verbatim inside \fbox{}**: LaTeX 的 `verbatim` 环境不能放在 `\fbox{...}` 的参数内部。`\fbox` 在读取参数时已经改变了 catcode，导致 `\begin{verbatim}` 无法正确激活逐字模式。修复：移除 `\fbox{}` 包裹，仅保留 `minipage` 环境。例如将 `\fbox{\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}}` 改为 `\begin{minipage}...\begin{verbatim}...\end{verbatim}\end{minipage}`。
- **Unicode in LaTeX**: 即使添加了 `inputenc`，某些 Unicode 字符（如 ≈ →）仍需手动替换为 LaTeX 命令。
- **graphicspath bracket matching**: `\graphicspath` 需要双花括号 `{{path/}}`。替换时如果原始路径包含多个目录（如 `{{figures/},{pics/}}`），正则替换必须确保括号配对正确。
- **Algorithmic package compatibility**: `algorithmic` 包在某些环境下（如 elarticle + MiKTeX特定版本）可能与 preamble 中的其他宏包冲突。如果报错 `algorithmic undefined`，直接删除算法环境是最安全的修复方式。
- **Backup-before-destructive**: 任何涉及 `rm`、`cp`、或批量 `replace` 的操作前，必须备份原始文件。`paper.*` 通配符会匹配 `paper.tex`。
- **State-score staleness**: paper-repair cron 生成的 state.json 可能包含过期的 quality_score。修复流程：先检查 quality-report.md 提取 Layer B 分数，用该分数更新 state.json。如果 quality_score >= 80，gate_status 改为 PASS，stage 改为 quality_check_complete。

## 参考文件

- references/latex-error-checklist.md — 完整错误分类速查表
- references/paper-compile-checklist.md — 每次编译前检查清单
- references/symlink-path-trap-01-manuscript.md — 01-manuscript/ 符号链接路径陷阱（2026-06-18 实战）
- scripts/latex-auto-fix.py — 自动检测和修复常见LaTeX错误的脚本

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。