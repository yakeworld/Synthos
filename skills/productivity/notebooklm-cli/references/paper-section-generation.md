# NotebookLM Q&A → Paper Section Generation

## 用途
通过NotebookLM `ask` 逐步生成SCI论文的每个IMRaD章节。每节单独Q&A，不一次全抛。

## 原理
NotebookLM的源文件底座（PDF文献+代码+markdown）是论文内容的基础。通过每节一个聚焦提问，确保每段内容都能追溯到源文件证据。跳过NotebookLM直接写论文会导致内容脱离源文件、虚构数据、语言混杂。

## 四节Q&A模板

### P2.1 Introduction（引言）

提问模板：
```
请基于项目所有源文件，用SCI标准IMRaD格式写出完整的Introduction部分——包括:
1) Background段落：[主题]的全球/临床背景
2) Related Work分段：现有[类1]方法、[类2]方法、[类3]方法的成就与局限
3) Gap段落：[具体悖论]的[具体原因数]个根本原因
4) Contribution列表：编号列出本文的4-5个贡献
5) 对比表（Comparison Table）：表格对比ours与代表系统在[维度1]/[维度2]/[维度3]等维度
请全部用LaTeX格式输出，所有内容使用英文
```

### P2.2 Methods（方法）

提问模板：
```
请用LaTeX格式写出论文Methods部分，需要包含:
1) 数据集描述：[名称]的[样本数]个样本、[特征数]个特征、统计分布、缺失情况
2) [框架名称]架构：核心原理和组件
3) 数据预处理协议：[具体步骤]
4) [关键算法]协议：[参数设置]
5) 交叉验证设计：[折数]-fold [类型]
6) 模型集合：[模型数]个基线模型，来自[库名]
7) [集成策略]：[具体方法]
8) [分析方法]：[工具和参数]
9) 消融实验设计：[层级数]级设计
请全部用LaTeX输出，内容用英文
```

### P2.3 Results（结果）

提问模板：
```
请用LaTeX格式写出论文Results部分。铁律：只呈现数据，不解释（解释归Discussion）。
需要包含:
1) 实验设置简述（[CV设置]，[模型数]个模型）
2) 表1：[具体内容]性能排名（列：[指标列表]），数据来源自项目实际运行结果
3) 消融实验结果：[对比设置]
4) [最优模型]结果：[具体数值]
5) [分析]结果：[特征排名]
请引用实际数据，不要使用占位符。全部用英文。
```

### P2.4 Discussion + Conclusion（讨论+结论）

提问模板：
```
请用LaTeX格式写出论文Discussion和Conclusion部分。

Discussion需要包含:
1) 主要发现解读：[核心结论的解读]
2) 与已有工作的对比讨论：[关键对比]
3) Limitations（编号，至少3条）：[列出局限]
4) [启示]

Conclusion需要包含:
1) 总结贡献
2) 核心结果重申
3) 未来工作：[具体方向]
4) Code Availability声明

请全部用LaTeX输出，内容用英文
```

## 组合编译流程

```bash
# 1. 写主paper.tex合并所有章节
write_file paper.tex  # elsarticle preamble + \input各节

# 2. 编译验证
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex

# 3. 质量检查
grep -c 'undefined' paper.log   # 应=0
grep -c 'Overfull' paper.log     # 越小越好
```

## 已知陷阱

1. **NotebookLM clear 丢上下文**：`notebooklm clear` 会重置notebook上下文。正确顺序是 `notebooklm use <id>` 后跟 `notebooklm ask` 在同一命令，或 `use` 确认成功后才 `clear`，再 `use` 再 `ask`。
2. **CJK + elsarticle不兼容**：elsarticle文档类不支持中文字符。如果论文部分内容有中文，编译报 `Unicode character not set up for use with LaTeX`。修复：翻译为纯英文。
3. **SubAgent/DelegateTask绕过NotebookLM**：使用delegate_task写完整论文会跳过NotebookLM内容底座，导致编造数据/内容偏离。必须通过NotebookLM Q&A生成每节内容，保存后再组合。
4. **LaTeX格式退化**：Q&A生成的LaTeX有时缺少`\begin{frontmatter}`/`\end{frontmatter}`包装或`\bibliography{}`声明。需要检查并在组合时补充。
