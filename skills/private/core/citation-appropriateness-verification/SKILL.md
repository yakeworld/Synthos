---
name: citation-appropriateness-verification
description: 逐篇阅读参考文献全文，对比论文引用语境，验证引用是否恰当、充分、准确。引文功能分类 + 引文网络分析 + 引文性能基准提取。独立于G5形式检查（DOI/D10a），专注于引用实质质量。
version: 3.1.0
priority: P0
related_skills: [quality-gate, paper-references-scanning, reference-verification, pdf-download-racing]
signature: "citation-appropriateness-verification -> processed_result"
---

# 引用恰当性审查

> 文言：引不验则废，引不证则诬，引不衡则偏。

## 核心原则

**三层引用检查**，从浅到深：

| 层 | 检查内容 | 对应技能 | 我们已做 |
|:---|:---------|:---------|:---------|
| L1: 引用存在性 | 引用是否真实存在（有 PDF / SS 可查） | reference-verification | ✅ |
| L2: 引用形式完整性 | D10a, DOI, orphan, zombie | paper-references-scanning | ✅ |
| **L3: 引用实质恰当性** | **PDF全文比对引用语境，验证论断支撑度** | **本技能** | **✅ 有报告但未系统化** |

## 四层引用分析

### 第一层：引用功能分类

每篇引用在论文中扮演什么角色？目前只判"恰当/不恰当"，可以更精细：

```
引用功能分类树:
├── 背景型 (Background)
│   ├── 领域综述: "糖尿病影响5亿人" → IDF2021
│   └── 概念定义: "数据泄露的定义" → Kapoor2023
├── 方法型 (Method)
│   ├── 工具引用: "我们使用SHAP分析" → Lundberg2017
│   ├── 算法引用: "SMOTE算法" → Chawla2002
│   └── 数据引用: "PIDD数据集" → Smith1988
├── 支撑型 (Support) ← 最重要的类型
│   ├── 直接支撑: "与我们的结果一致" → 提供实证
│   ├── 对比支撑: "与XXX相反" → 提供反例
│   └── 理论支撑: "理论基础" → 提供框架
├── 争辩型 (Argument)
│   ├── 靶子引用: "这些论文声称99%准确率" → 批驳对象
│   ├── 空白声明: "尚无标准化协议" → 研究缺口
│   └── 局限声明: "如XXX指出的" → 知情承认
└── 装饰型 (Decorative) ⚠️
    ├── 堆砌引用: 一段话引5篇，无具体支撑
    └── 冗余引用: 引了原始论文又引综述
```

**判定规则**：
- 一篇引用可以承担多个功能（SHAP论文既是Method又是理论支撑）
- 但如果一篇引用在论文中只有**Decoration**功能 → 建议删除或移到适当位置
- Core Claim 的支撑型引用必须有 ≥2 篇直接证据

### 第二层：引文性能基准提取

逐篇读PDF时，除了验证引用是否恰当，还提取每篇论文报告的**性能指标**：

```python
# 从30篇被引论文中提取性能数据
performance_database = {
    "Smith1988":   {"dataset": "PIDD", "acc": 76.0,  "method": "ADAP",       "note": "原始PIDD论文"},
    "Akbar2023":   {"dataset": "PIDD", "acc": 99.60, "method": "SMOTE+KMeans", "note": "高acc声称，泄露可疑"},
    "Talari2024":  {"dataset": "PIDD", "acc": 99.14, "f1": 0.99, "method": "CSSF+SMOTE", "note": "高acc声称，泄露可疑"},
    ...
}
```

**用途**：
| 用途 | 说明 |
|:-----|:------|
| 构建 Table 1 文献对比表 | 直接来自PDF的Acc/F1/Sen/Spe，非LLM编造 |
| 检测论文声称是否合理 | 如果论文声称"所有研究都>95%"，但实际提取的基准显示大多数<80% → 论文夸大 |
| SOTA 天花板判定 | 从所有PIDD论文中提取最大Acc/F1，确定真实性能上限 |

### 第三层：引文网络分析

所有被引论文之间的关系：

```text
[Kapoor2023] ──批评──→ [Akbar2023, Talari2024]  (高acc=数据泄露)
[Smith1988]  ──被引用──→ [Chawla2002, Vanschoren2014] (数据+工具)
[Lundberg2017] ──被引用──→ [本文SHAP分析] (方法)
[PROBAST]    ──对齐──→ [本文CRISP-DM Helix] (框架)
```

**可提取的信息**：
- 论文的核心引文网络密度（引用间互相引用的比例）
- 孤立引用（不与任何其他被引论文关联）→ 可能是装饰引用
- 争议簇（引用了互相矛盾的论文群组）→ 论文是否平衡呈现？

### 第四层：引用缺失分析

读完所有引文的全文后，能发现**应该引用但没引**的论文：

| 信号 | 含义 |
|:-----|:------|
| 论文讨论X问题但引文中无X领域经典文献 | ⚠️ MISSING_CORE_REFERENCE |
| 论文方法Y来自特定工具但无原始论文引用 | ⚠️ MISSING_METHOD_REFERENCE |
| 论文声称"现有研究都做Z"但引文不支撑 | ⚠️ GAP_OVERCLAIM |
| 引文集中在少数期刊/年份 | ⚠️ CITATION_BUBBLE |

---

## 执行流程

### Codex 协议

此任务适合通过 tmux 发送给 Codex CLI 处理（逐篇读PDF + 逐行比对，长计算非阻塞）。

```bash
tmux send-keys -t codex-quality '请读取 /tmp/citation_task.md 并执行' Enter
```

### 输入

```
paper_dir: str  # 论文目录路径（含01-manuscript/paper.tex, 06-references/, references.bib）
```

### 输出

报告结构（与通用六域报告并行）：

```
═══════════════════════════════════════════════
  参考文献审查专项报告
═══════════════════════════════════════════════

【引文功能分类】
  背景型:   N篇 (合理范围: 10-40%)
  方法型:   N篇 (合理范围: 20-40%)
  支撑型:   N篇 ← 核心指标，应占多数
  争辩型:   N篇
  装饰型:   N篇 ← ⚠️ 应接近0

【引文性能基准 (PIDD)】
  ┌────────────────────────────────────────┐
  │ 来源            Acc      F1     泄露  │
  ├────────────────────────────────────────┤
  │ Akbar2023      99.60    —      🔴    │
  │ Talari2024     99.14    0.99   🔴    │  
  │ Smith1988      76.00    —      ✅    │
  │ Ours           **77.59** 0.707  ✅    │
  └────────────────────────────────────────┘
  天花板: Acc=76.0% (无泄漏基线), F1上限≈0.71
  高Acc声称: 8/12 篇存在数据泄露 → 验证论文"Selective Inflation"论点

【引文网络分析】
  核心引文簇: Kapoor2023 → PROBAST → TRIPOD (论证链闭合)
  孤立引用: Chang2024 (无其他引文关联) → ⚠️ 可能是装饰引用
  缺失引用: 无 (覆盖完整)

【引用恰当性判定】
  ✅ 完全恰当:  28/32
  ⚠️ 部分恰当:  3/32 (引用合理但语境略宽泛)
  ❌ 不恰当:     1/32 (装饰引用, 建议删除)
  
  引用恰当率: 87.5% (高于阈值80%)
═══════════════════════════════════════════════
```

### 输出文件

与通用六域报告和类型专项报告并排放置：

```
07-quality/
├── report-domain-general.md          # 通用六域报告
├── report-clinical-ml.md             # 临床ML专项
├── report-citations.md               # ← 参考文献审查专项报告（本技能产出）
└── fix-log.md                        # 修复日志
```

---

## 与 quality-gate 的集成

在 quality-gate G5 引用质量门中：

```
G5 引用质量门:
  ├── 形式检查 → paper-references-scanning (D10a, DOI, orphan, zombie)
  ├── PDF验证 → reference-verification (PDF存在性, DOI匹配)
  └── 实质检查 → **本技能** ← 加入G5作为必经步骤
       ├── 引用功能分类
       ├── 引文性能基准提取
       ├── 引文网络分析
       └── 引用缺失分析
```

**G5通过条件更新**：
- 旧：D10a ≥ 95%, 0 orphan, 0 zombie
- 新：D10a ≥ 95% AND 引用恰当率 ≥ 80% AND 装饰引用 ≤ 10%

---

## 执行工具链 · API 故障恢复

**优先级顺序**：
1. Semantic Scholar API（SS）→ 最快，返回结构化数据（标题、作者、引用数、PDF链接、开放获取）
2. **Crossref API** → 备用，需手动构建 BibTeX。注意：**Crossref 不再支持 `format=bibtex` 参数**，必须用 JSON 响应手动构造 BibTeX
3. **PubMed/NCBI E-utilities** → 医学/生物医学领域首选。使用 `esearch.fcgi` + `esummary.fcgi` 两步法
4. **Crossref 失败时** → PubMed，再失败则标记为 `MISSING`

**关键限制**：
- **Crossref 查询长度 ≤ 160 字符**：超过 160 字符返回 HTTP 400 Bad Request。必须截断
- **Semantic Scholar API Key 可能失效/限流**：SS Key 过期后返回 429，必须自动回退到 Crossref/PubMed
- **SS 无 API Key 时**：返回空结果（0 篇），必须检测并切换策略

**BibTeX 生成陷阱**（2026-07-01 修复）：
- 条目键名（cite key）**不应包含 `{` 或特殊字符**：错误格式 `@article{spalton2014computational{` → 正确格式 `@article{spalton2014computational`
- **标题截断**：某些 API 返回的 title 字段被截断（只有一半），需验证标题长度 ≥ 20 字符
- **abstract 字段不应出现在 BibTeX 中**：BibTeX 标准不包含 abstract 字段
- **journal 字段错误**：某些自动恢复脚本将 year 写入 journal 字段
- **自引用检测**：新引用标题与论文自身标题高度相似 → 可能是自引用，需人工确认

## API Key 管理

- **Semantic Scholar API Key**: `iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt`（40字符，无前缀）
- **存储位置**: `~/.secrets`（mode 600）
- **`.bashrc`**: `s2k-HT...TmBD` 是**占位符**，非真实 key
- **`s2k-` 前缀**: 全部已过期，返回 403 Forbidden。SS 接受两种格式（无前缀 / `s2k-` 前缀），但 `s2k-` 已全部废弃
- **无 `.env` 文件包含 SS Key**: 所有 `.env` 文件中的值为 `***` 或模板占位符
- **环境变量隔离**: 子 shell 不自动 source `~/.secrets`，脚本中必须显式 source 或 export。错误表现：API 返回空结果/429
- **PubScholar 正确地址**: `pubscholar.cn`（非 `nfschina.com`）

## API 故障恢复增强

- **Semantic Scholar**: 1 request/second max. 绝不并行调用 SS
- **Crossref**: 查询长度 ≤ 160 字符，需截断
- **PubMed/NCBI**: 推荐每10秒调用1次（NCBI 建议）

## 参考文献重建流程（2026-07-01 新增）

当论文原始参考文献全部丢失时，按以下流程重建：

1. **读取完整 paper.tex** — 提取所有研究主题、方法、问题
2. **提取研究空白和科学假设** — 从引言/讨论/结论中定位
3. **按领域批量检索** — 6+个领域，每个领域用 PubMed+Crossref 搜索
4. **生成 DOI 映射** — 为原始 `\cite{}` 键生成匹配的 DOI 条目
5. **保留原始引用键** — BibTeX 条目使用原始引用键名（如 `\cite{Raissi2019}` → `@article{Raissi2019}`）
6. **处理失败** — issue-level DOI、服务器500错误需特殊处理

## Change Log

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-07-01 | 3.1.1 | 修正 Crossref 查询长度限制（100→160字符，实际 API 限制为 160）。 |（SS key 存储位置、占位符识别、子 shell 隔离问题）。新增参考文献重建流程。PubScholar 正确地址修正。 |
| 2026-07-01 | 3.0.0 | API 故障恢复策略：SS→Crossref→PubMed 三级回退。新增 Crossref 查询长度限制（100字符）和 BibTeX 生成陷阱。Crossref 不再支持 format=bibtex。 |
| 2026-06-24 | 2.0.0 | 从 quality-gate 拆分为独立技能。新增引用功能分类树（6类）、引文性能基准提取、引文网络分析、引用缺失分析。 |
| 2026-06-24 | 2.1.0 | 重构输出格式为独立专项报告，与通用六域报告并行。新增 G5 集成点。 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Citation Appropriateness Verification

