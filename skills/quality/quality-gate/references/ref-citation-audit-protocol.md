# 参考文献引用审计协议

> 核心规则：**凡引必验，不验不刊。**
> 每篇引用必须有全文PDF或DOI可访问，引用内容必须与原文一致，数值声明必须追溯到原文。

---

## 一、审计清单（必检6项）

### ✅ 1. 引用覆盖率 | 无孤儿无僵尸

| 检查项 | 命令 | 通过条件 |
|:-------|:-----|:---------|
| Bibitem计数 | `grep -c '\\\\bibitem{' paper.tex` | ≥30（投稿级≥40） |
| 唯一引用数 | `grep -oP '\\\\cite{([^}]+)}' paper.tex \| sed 's/cite{//;s/}//' \| tr ',' '\\n' \| sed 's/^ *//' \| sort -u \| wc -l` | 每篇bibitem至少被引1次 |
| 僵尸引用 | 如上，取 (bibitems - used_cite) | 0 |
| 孤儿引用 | 取 (used_cite - bibitems) | 0 |

```bash
# 一键检查
bibitems=$(grep -c '\\\\bibitem{' paper.tex)
used=$(grep -oP '\\\\cite{([^}]+)}' paper.tex | sed 's/cite{//;s/}//' | tr ',' '\n' | sed 's/^ *//' | sort -u | wc -l)
echo "bibitems: $bibitems, unique_cited: $used"
# 僵尸：bibitems中的key不在used中
# 孤儿：used中的key不在bibitems中
```

### ✅ 2. DOI完整性

| 检查项 | 方法 |
|:-------|:-----|
| DOIs缺失率 | `grep -c 'doi\\|DOI' paper.tex` vs bibitem数 |
| DOI可访问性 | `curl -sI "https://doi.org/10.xxxx/xxxxx" \| head -1` 应返回 200/302 |
| DOI前缀-期刊匹配 | 见 `references/bibtex-doi-audit.md` 类型B |

**规则**：LaTeX `thebibliography` 环境中每篇应包含 `doi={...}` 字段，或统一使用 `.bib` 文件管理。

### ✅ 3. PDF全文存在性

每篇引用须满足以下之一：
- 本地PDF存储于 `03-code/refs/` 或项目参考目录
- 有可访问的DOI（可通过 `doi.org` 获取全文）
- 有arXiv ID（可通过 `arxiv.org` 获取全文）
- 经典著作/教科书（需特别标注）

**PDF验证**：`file your.pdf` 确认 `%PDF-` 头 + `pdfinfo` 确认元数据与bibitem一致

### ✅ 4. 引用数值准确性（L0.5扩展检查）

对论文中所有**可验证的数值声明**，逐条追溯引用源：

| 声明模式 | 示例 | 追溯方法 |
|:---------|:-----|:---------|
| "X报告了Y值=Z" | "Bradshaw2010 RMSE=0.08mm" | 查PDF中Table/正文该数值 |
| "据Y报道，范围是Z" | "cochlear spiral b≈0.02-0.08" | 查PDF中Figure/Table |
| "达到Z精度" | "sub-pixel accuracy" | 查PDF中Methods/Results |
| "数据显示Z趋势" | "elliptical shape increases drag 1.4×" | 查PDF中Results/Discussion |

**违规标记**：
- 数值在原文中找不到 → 🔴 虚构引用
- 数值来自间接引用（A引B但论文归到A）→ 🟡 引用链漂移
- 数值被夸大或方向反转 → 🔴 叙事驱动数据

### ✅ 5. 引用上下文适当性

| 检查项 | 判定 |
|:-------|:-----|
| 教科书作为原始数据来源 | ⚠️ 建议替换为原始研究 |
| 综述作为研究空白证据 | 🟡 可接受但应辅以原始研究 |
| 自引过多（>30%） | ⚠️ 需平衡 |
| 引用年份与声称时序一致 | ✅ 原始研究应早于声称时间 |

### ✅ 6. BibTeX格式规范（如使用.bib）

```bash
# 检查bib条目数 vs 有DOI的条目数
bib_count=$(grep -c '^@' references.bib 2>/dev/null || echo 0)
doi_count=$(grep -c -i 'doi\\s*=' references.bib 2>/dev/null || echo 0)
echo "DOI覆盖率: $doi_count/$bib_count"

# 检查重复DOI
grep -oP 'doi\\s*=\\s*\\{[^}]+\\}' references.bib | sort | uniq -d

# 检查PDF元数据与bib一致性
# 见 references/bibtex-doi-audit.md
```

---

## 二、审计报告模板

每次审计后生成 `ref-audit-report.md`：

```markdown
# 参考文献审计报告

## 摘要
| 维度 | 结果 | 判定 |
|:-----|:-----|:----:|
| 引用总数 | N篇 | — |
| 僵尸引用 | N | 0 ✅ / >0 ❌ |
| 孤儿引用 | N | 0 ✅ / >0 ❌ |
| DOI完整性 | NN/N | ≥80% ✅ / <80% ❌ |
| 本地PDF | NN/N | ≥80% ✅ / <80% ❌ |
| 数值准确性 | NN篇已验/NN篇待验 | — |

## 僵尸/孤儿引用
- ❌ Sieber2019 — 在bib但正文未引

## 缺失DOI列表
- Rabbitt2019 (doi: 需补)

## 数值声明待验证
| 声明 | 引用 | 风险 | 核实结果 |
|:-----|:-----|:----:|:---------|
| "RMSE=0.08mm" | Bradshaw2010 | 🔴 待PDF确认 | — |
| "椭圆度0.74" | Ifediba2007 | 🟡 待PDF确认 | — |

## 修复记录
| 问题 | 修复方式 |
|:-----|:---------|
| Sieber2019 僵尸引用 | 在§2.3添加\cite{} |
```

---

## 三、执行时机

| 时机 | 动作 | 负责人 |
|:-----|:-----|:-------|
| 论文编译成功后 | 自动执行6项检查 | Hermes Agent |
| 新增/修改引用后 | 验证新引用完整性 | Hermes Agent |
| 最终投稿前 | 全量PDF+数值交叉验证 | 人工 + Agent |
| 审稿人质疑引用时 | 提供审计报告 | Hermes Agent |

---

## 四、实战教训案例

### 案例1：引用链漂移（2026-05-25）
- 问题：EllSeg IoU=0.9618 被引用为 kothari2021ellseg，实际该值来自 jia2024condseg 的复现实验
- 修复：改引用为实际来源

### 案例2：僵尸引用（2026-05-30，本次）
- 问题：Sieber2019 在bibliography但正文无一处 `\cite{Sieber2019}`
- 根因：添加文献到列表后忘记在正文插入引用
- 修复：在 §2.3 数据来源描述处补充

### 案例3：教科书代替原始文献
- 问题：Epp2010 被用来引用cochlear螺旋率数据，但该数据实际来自 Manoussaki2008
- 建议：保留原始研究引用，移除教科书引用

### 案例4：无DOI无PDF（本次发现）
- 问题：全部43篇参考文献均无DOI字段，本地无PDF
- 风险：审稿时无法快速验证
- 建议：转换为BibTeX格式，逐篇补DOI和PDF
