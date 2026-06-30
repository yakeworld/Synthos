# 论文 .bib 文件恢复工作流

> 记录时间: 2026-06-30
> 来源: Synthos 论文管线 .bib 丢失事故复盘

## 事故背景

在论文目录标准化过程中，`06-references/` 目录（包含所有论文的 .bib 文件和参考文献 PDF）被删除，导致约 9-10 篇论文丢失参考文献元数据。

## 关键区分

**两种不同的丢失问题必须分开处理：**

| 类型 | 内容 | 影响 | 优先级 |
|------|------|------|--------|
| **.bib 丢失** | 参考文献元数据（作者、标题、期刊、DOI） | paper.tex 引用键无对应条目，编译时有 warning，References 章节空白 | **高** — 影响 D10a |
| **PDF 丢失** | 参考文献全文 PDF（06-references/ 为空） | 无法快速查阅引用内容 | **中** — 不影响编译 |

**06-references 为空 ≠ 丢失 .bib**。06-references 主要放 PDF。但实际中 .bib 也可能在 06-references/ 或 01-manuscript/ 中。需要逐一检查。

## 恢复流程

### 步骤 1：全量扫描

遍历所有论文目录（不仅仅是已知缺失的 9 篇），检查每篇论文的 .bib 完整性：

```bash
# 对每篇论文检查：
# 1. 是否有 .bib 文件（01-manuscript/ 或 06-references/）
# 2. paper.tex 引用了多少条 (\cite{key})
# 3. .bib 覆盖了哪些
# 4. 输出完整报告
```

**不要假设只有 9 篇缺失**。扫描所有 88 篇论文。

### 步骤 2：从 _archive 翻找

深度扫描 `_archive/` 目录树，找旧结构的 .bib 文件：

```
_media/yakeworld/sda2/Synthos/_archive/
  system/
    submissions/journals/        ← 部分 .bbl 和 .bib 可能在这里
    _knowledge_only/             ← 旧结构快照
    drafts_archive/              ← 可能包含原始论文目录
```

已知发现：
- `smooth-pursuit-PINN` 的 references.bib 在 `drafts_archive/papers/97-smooth-pursuit-ODE/`
- `pima-crispdm` 的 references.bib 在 `submissions/journals/pima-crispdm/references.bib`

### 步骤 3：Crossref API 批量恢复

对无法从 _archive 恢复的论文：

1. 从 `paper.tex` 的 `\cite{key}` 提取所有引用键
2. 从 thebibliography 环境提取每条参考文献的完整文本（作者、标题、期刊、年份）
3. 用标题+年份在 Crossref API 搜索匹配 DOI
4. 找到后获取完整 `.bib` 条目
5. 保存到对应论文的 `06-references/references.bib`

**注意事项**：
- 标题可能有拼写误差，匹配率不确定
- 非期刊文献（会议、书籍、报告）Crossref 覆盖率低
- 恢复的每条引用必须标注来源：`[crossref]` / `[backup]` / `[manual]`

### 步骤 4：验证与审计

1. 对每篇恢复的 .bib，运行 pdflatex 编译验证无 undefined reference
2. 标记每个条目的来源
3. 运行 G5（reference quality）门检查

## 优先级框架

| 优先级 | 论文 | 恢复方式 | 复杂度 |
|--------|------|----------|--------|
| P0（立即） | 有 .archive 备份的 | 直接复制 | 分钟级 |
| P1 | 内联 thebibliography 大部分完整（如 cupula 17/20） | 补充缺失 | 30分钟 |
| P2 | 引用数 < 15 的 | Crossref 快速匹配 | 30分钟 |
| P3 | 引用数 > 25 的 | Crossref 批量，每篇 5-15分钟 | 30-90分钟 |

## 执行纪律

1. **先扫描，后操作**：全量扫描报告是决策基础
2. **每篇独立验证**：恢复后必须编译通过
3. **来源标注**：每条引用标注 [backup]/[crossref]/[manual]
4. **安全操作**：任何文件操作前确认有备份或确认是新增
5. **记录到 08-records/recovery-log.md**：每篇恢复的记录
