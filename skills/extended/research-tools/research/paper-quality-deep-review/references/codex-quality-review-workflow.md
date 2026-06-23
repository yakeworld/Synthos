# Codex --yolo 论文质量审查工作流

> 当 `codex exec` 因沙箱问题失败时，使用 `--yolo` 绕过沙箱。
> 本文件记录两阶段流程：审查 → 修复。

## 阶段一：质量审查

### 指令模板

```bash
cat << 'PROMPT' | codex --yolo exec --skip-git-repo-check
对论文进行完整质量评估，输出中文 Markdown 报告。

论文目录: /path/to/paper
论文文件: 01-manuscript/paper.tex
参考文献: references.bib
实验代码: 03-code/experiment/

评估要求（按优先级）:

P0 - 逐篇文献验证:
1. 提取 paper.tex 中所有 \cite{} 引用
2. 提取 references.bib 中所有条目信息
3. 对每篇引用文献，检查: 上下文是否与标题一致、引用理由是否合理、DOI是否规范
4. 列出所有问题引用
5. 检查 bib 中有但未引用的条目

P1 - 跨数据集验证检查:
1. 检查 cross_dataset_results.json 数据与论文 Table 是否一致
2. PIDD 核心结果与实验代码是否一致

P2 - G1-G7 质量评分

P3 - 格式与润色

输出到 07-quality/xxx.md
PROMPT
```

### 数据库文献交叉检查步骤

1. 扫描 `03-code/` 目录的 `.py`/`.ipynb` 文件，查找数据集加载模式：
   - `load_breast_cancer()` → WDBC
   - `pd.read_csv('*diabetes*')` → 各种糖尿病数据集
   - `fetch_*` → sklearn/sklearn 内置数据集
2. 对每种数据集，检查论文是否有对应的原始文献引用
3. 常见缺失：WDBC→Wolberg1990, CDC BRFSS→原始 CDC 文献, NHANES→原始 NHANES 文献

### 每篇引用的评估格式

```
### ✅/⚠️ KeyName — 文献标题

- **作者**: ...
- **标题**: ...
- **期刊/年份**: ...
- **DOI**: ...
- **引用上下文**: (论文中的原始引用段落)
- **评估**: 🟢准确 / 🟡部分问题 / 🔴错误
- **问题**: 具体问题描述
```

## 阶段二：审查后修复

### 引用修复流程

1. **DOI 可疑**（如 Akbar2023 的 DOI 格式不匹配期刊）→ 改用文本引用 `(Author et al., Year)` 替代 `\cite{}`
2. **bib 重复**（如 Kapoor2023Leakage 出现两次）→ 删除第二条
3. **bib 中未引用的条目** → 前缀 `%UNUSED-` 标记保留
4. **"92% PIDD 研究"类无支撑声明** → 替换为泛述
5. **Varoquaux 等语境不精确的引用** → 明确说明每篇文献的具体贡献

### bib 清理命令

```bash
# 提取所有引用键
grep -oP 'cite\{[^}]+\}' paper.tex | grep -oP '\{[^}]+\}' | tr -d '{}' | tr ',' '\n' | sort -u > /tmp/cited.txt

# 提取所有 bib 键
grep -oP '^\s*@\w+\{\K[^,]+' references.bib | sort -u > /tmp/bib_all.txt

# 找到未引用的 → 标记 
while read key; do
  if ! grep -q "$key" paper.tex; then
    sed -i "/^@article{$key\b\|^@misc{$key\b\|^@book{$key\b}/s/^/%UNUSED-/" references.bib
  fi
done < /tmp/bib_all.txt
```

### LaTeX 反斜杠污染修复

当 patch 工具产生双反斜杠时（`\\\\item` 而非 `\item`）：

```bash
sed -i 's/\\\\cite/\\cite/g; s/\\\\textbf/\\textbf/g; s/\\\\begin/\\begin/g; s/\\\\end/\\end/g; s/\\\\label/\\label/g; s/\\\\%/\\%/g' paper.tex
```
