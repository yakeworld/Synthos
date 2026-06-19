---
name: paper-quality-deep-review
description: 论文质量深度审查引擎 — 从文献下载→内容分析→研究空白验证→科学假设评估→解决方法评估→文献引用质量评分→综合评分。
version: 1.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: "End-to-end paper quality deep review — from literature download through content analysis, gap validation, hypothesis assessment, method evaluation, citation quality scoring to comprehensive quality grading."
    signature: "paper_path: str -> deep_review_report: dict"
    related_skills:
      - knowledge-acquisition
      - knowledge-extraction
      - association-discovery
      - hypothesis-generation
      - argument-expression
      - viewpoint-verification
      - pdf-download-racing
      - paper-pipeline
---
## IO_CONTRACT

- **input**: `paper_path: str, review_mode: str = "full"` — 论文路径与审查模式
- **output**: `deep_review_report: dict` — 包含 G1-G7 评分、研究空白、假设、改进建议

> 对应原则：P2（机械原子暴露输入输出规范）


# 论文质量深度审查引擎 (Paper Quality Deep Review Engine)

## 核心定位

> **论文质量审查不是格式检查，而是实质审查。**
> 每篇引用必须验证其引用理由；每个研究空白必须验证其存在性；每个假设必须验证其可证伪性；每个方法必须验证其科学性和先进性。

## 审查流程

```
输入: paper_path (包含 paper.tex, references.bib, data/, code/)
  ↓
Step 1: 文献下载与内容提取
  ├── 使用 pdf_download_engine.py 下载所有参考文献 PDF
  ├── 逐篇提取每篇文献的摘要、方法、结果、讨论
  └── 提取每篇文献的引用理由（context in the paper）
  ↓
Step 2: 文献引用深度验证（凡引必验）
  ├── 逐篇验证：该文献是否真的支持论文中的引用主张？
  ├── 引用上下文是否准确？有无断章取义？
  ├── 引用理由是否合理？有无误导性引用？
  └── 生成引用质量评分（每篇 0-10 分）
  ↓
Step 3: 研究空白验证（CARS模型）
  ├── 识别论文的 Introduction 逻辑链：背景→缺口→空白
  ├── 验证每个空白声明是否有文献支撑
  ├── 独立检索最新文献验证空白是否真实存在
  └── 评估空白的 新颖性、重要性、可研究性
  ↓
Step 4: 科学假设评估
  ├── 提取论文的核心科学假设
  ├── 评估假设的 可证伪性、新颖性、可行性、重要性
  └── 提出改进建议
  ↓
Step 5: 解决方法评估
  ├── 评估方法论的 科学性、先进性、可行性、可复现性
  └── 与现有方法对比（SOTA benchmark）
  ↓
Step 6: 文献引用质量评分
  ├── 评估引用文献的 权威性、相关性、时效性、多样性、完整性
  ├── 识别缺失的重要文献
  └── 建议补充参考文献
  ↓
Step 7: 综合评分与报告
  ├── 总体质量评分 (0-100)
  ├── 通过/不通过建议
  └── 具体改进建议
  ↓
输出: deep_review_report (JSON) + review_report.md (Markdown)
```

## 输入输出契约

### 输入

```json
{
  "paper_path": "/path/to/paper/directory",
  "review_depth": "basic | standard | deep",  // basic=仅格式, standard=内容+引用, deep=完整深度审查
  "include_references": true,  // 是否引用下载引擎和现有技能
  "generate_report": true,  // 是否生成报告文件
  "output_dir": "/path/to/output"  // 输出目录
}
```

### 输出

```json
{
  "paper_name": "paper-name",
  "review_date": "2026-06-20",
  "review_depth": "deep",
  "overall_score": 85.5,
  "grade": "B+",
  "recommendation": "ACCEPT",  // ACCEPT / MINOR_REVISION / MAJOR_REVISION / REJECT
  "sections": {
    "citation_validation": {
      "score": 78.0,
      "total_refs": 30,
      "verified_refs": 28,
      "problematic_refs": 2,
      "ref_details": [
        {
          "key": "Author2020",
          "claim": "该文献报告99%准确率",
          "verification": "部分支持 — 但99%是特定条件下的结果",
          "score": 7.0,
          "issues": ["条件性结果未说明实验条件"],
          "recommendation": "补充实验条件说明"
        }
      ]
    },
    "gap_validation": {
      "score": 90.0,
      "gaps_identified": 3,
      "gaps_verified": 3,
      "gap_details": [
        {
          "claim": "现有方法缺乏可解释性",
          "supporting_literature": ["Cabitza2024", "Wen2022"],
          "independent_verification": "真实 — PubMed搜索确认",
          "novelty": "high",
          "importance": "high",
          "researchability": "high"
        }
      ]
    },
    "hypothesis_assessment": {
      "score": 82.0,
      "hypothesis": "HCS-3WT方法在乳腺癌诊断中优于传统ML方法",
      "falsifiability": 9.0,
      "novelty": 8.0,
      "feasibility": 9.0,
      "importance": 8.0,
      "average_score": 8.5,
      "suggestions": ["明确反证条件", "补充实验设计"]
    },
    "method_assessment": {
      "score": 86.0,
      "scientificity": 9.0,
      "advanced": 8.0,
      "feasibility": 9.0,
      "reproducibility": 8.0,
      "average_score": 8.5,
      "sota_comparison": "优于传统CNN但慢于轻量级方法",
      "suggestions": ["补充与SOTA方法对比实验"]
    },
    "citation_quality": {
      "score": 80.0,
      "authority": 8.0,
      "relevance": 9.0,
      "timeliness": 7.0,
      "diversity": 8.0,
      "completeness": 7.0,
      "missing_papers": ["建议补充2025-2026年最新文献"],
      "suggestions": ["补充最新引用", "增加中文文献"]
    }
  },
  "final_recommendation": "ACCEPT with minor revisions",
  "critical_issues": [
    "引用中2篇文献的引用理由需要更精确表述",
    "建议补充2025-2026年最新文献"
  ],
  "improvement_suggestions": [
    "修改引言中第2段的空白声明，使其更精确",
    "补充与SOTA方法的对比实验",
    "补充最新文献引用（2025-2026）"
  ]
}
```

## 审查标准

### 引用质量评分标准

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 权威性 | 30% | 期刊影响因子、被引次数、作者声誉 |
| 相关性 | 25% | 与论题的直接关联度 |
| 时效性 | 20% | 是否包含最近3年的文献 |
| 多样性 | 15% | 是否涵盖多个学派/方法/观点 |
| 完整性 | 10% | 是否有重要文献未引用 |

### 引用内容验证标准

| 级别 | 分数 | 标准 |
|------|------|------|
| 完全支持 | 10 | 文献明确支持引用主张，无歧义 |
| 部分支持 | 8-9 | 文献部分支持引用主张，有条件性 |
| 勉强支持 | 6-7 | 文献勉强支持引用主张，需解释 |
| 不支持 | 4-5 | 文献不支持引用主张，但可解释 |
| 错误引用 | 2-3 | 文献明确不支持引用主张 |
| 伪造引用 | 0-1 | 文献不存在或完全无关 |

### 研究空白评分标准

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 真实性 | 30% | 空白是否真实存在（独立验证） |
| 重要性 | 25% | 空白对该领域的重要性 |
| 新颖性 | 25% | 空白是否是新发现的 |
| 可研究性 | 20% | 空白是否可被研究方法填补 |

### 科学假设评分标准

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 可证伪性 | 30% | 是否有明确的反证路径 |
| 新颖性 | 25% | 假设是否是新提出的 |
| 可行性 | 25% | 假设是否可被实验验证 |
| 重要性 | 20% | 假设对领域的贡献 |

### 解决方法评分标准

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 科学性 | 30% | 是否遵循领域标准 |
| 先进性 | 25% | 是否优于现有方法 |
| 可行性 | 25% | 数据、资源是否充足 |
| 可复现性 | 20% | 代码、数据是否公开 |

## 依赖技能与工具

### 必须依赖

- **pdf-download-racing**: `skills/extended/research-tools/research/paper-retrieval/pdf-download-racing/SKILL.md`
  - 使用 `pdf_download_engine.py` 下载参考文献 PDF
  - 使用 `race_downloads()` 函数进行多源并发下载

- **paper-pipeline**: `skills/extended/research-tools/paper-pipeline/SKILL.md`
  - 使用 G1-G7 质量门禁作为参考
  - 使用论文管线流程作为参考

### 可选依赖

- **knowledge-acquisition**: `skills/core/knowledge-acquisition/SKILL.md`
  - 使用多源搜索获取相关文献

- **knowledge-extraction**: `skills/core/knowledge-extraction/SKILL.md`
  - 从 PDF 提取结构化知识

- **association-discovery**: `skills/core/association-discovery/SKILL.md`
  - 识别知识项间关系

- **hypothesis-generation**: `skills/core/hypothesis-generation/SKILL.md`
  - 基于分析生成可检验假设

- **argument-expression**: `skills/core/argument-expression/SKILL.md`
  - 构建学术论证链

- **viewpoint-verification**: `skills/core/viewpoint-verification/SKILL.md`
  - 多角度验证假设

## 执行步骤

### Step 1: 文献下载与内容提取

```python
# 使用 pdf_download_engine.py
from pdf_download_engine import download_scihub_direct, download_meddata, verify_pdf

# 1. 从 paper.tex 提取参考文献列表
bib_keys = extract_bib_keys('paper.tex')

# 2. 逐篇下载参考文献 PDF
for key in bib_keys:
    pdf = download_scihub_direct(key.doi) or download_meddata(key.doi, key.pmid)
    if pdf and verify_pdf(pdf):
        save_pdf(pdf, f'pdfs/{key}.pdf')
        # 3. 提取文献内容
        content = extract_pdf_content(f'pdfs/{key}.pdf')
        save_content(content, f'content/{key}.json')
```

### Step 2: 文献引用深度验证

```python
# 逐篇验证引用理由
def validate_citation(paper, ref_key, ref_context, ref_pdf_content):
    """验证一篇文献的引用理由"""
    
    # 1. 提取论文中的引用上下文
    context = extract_citation_context(paper, ref_key)
    
    # 2. 提取文献的内容
    pdf_content = extract_pdf_content(ref_pdf_content)
    
    # 3. 分析文献是否支持引用主张
    support = analyze_support(context.claim, pdf_content)
    
    # 4. 生成评分
    score = calculate_citation_score(support)
    
    # 5. 生成报告
    report = generate_citation_report(
        key=ref_key,
        claim=context.claim,
        support=support,
        score=score,
        issues=find_issues(context, pdf_content),
        recommendation=suggest_improvement(context, pdf_content)
    )
    
    return report
```

### Step 3: 研究空白验证（CARS模型）

```python
def validate_research_gap(paper, gap_claim, supporting_papers):
    """验证研究空白的存在性"""
    
    # 1. 提取空白的文献支撑
    evidence = extract_supporting_evidence(paper, gap_claim)
    
    # 2. 独立验证空白是否存在
    independent = independent_gap_verification(gap_claim)
    
    # 3. 评估空白的三个维度
    gap_assessment = {
        'truthfulness': assess_truthfulness(evidence, independent),
        'novelty': assess_novelty(evidence, independent),
        'importance': assess_importance(evidence, independent),
        'researchability': assess_researchability(gap_claim)
    }
    
    return gap_assessment
```

### Step 4: 科学假设评估

```python
def assess_hypothesis(paper, hypothesis):
    """评估科学假设的质量"""
    
    assessment = {
        'falsifiability': assess_falsifiability(hypothesis),
        'novelty': assess_hypothesis_novelty(hypothesis),
        'feasibility': assess_feasibility(hypothesis),
        'importance': assess_importance(hypothesis)
    }
    
    return {
        'hypothesis': hypothesis,
        'scores': assessment,
        'average_score': mean(assessment.values()),
        'suggestions': generate_hypothesis_suggestions(assessment)
    }
```

### Step 5: 解决方法评估

```python
def assess_method(paper, method):
    """评估解决方法的质量"""
    
    assessment = {
        'scientificity': assess_scientificity(method),
        'advancedness': assess_advancedness(method),
        'feasibility': assess_feasibility(method),
        'reproducibility': assess_reproducibility(method)
    }
    
    return {
        'method': method,
        'scores': assessment,
        'average_score': mean(assessment.values()),
        'sota_comparison': compare_with_sota(method),
        'suggestions': generate_method_suggestions(assessment)
    }
```

### Step 6: 文献引用质量评分

```python
def score_citation_quality(paper, references):
    """评分文献引用的质量"""
    
    scores = {
        'authority': score_authority(references),
        'relevance': score_relevance(references),
        'timeliness': score_timeliness(references),
        'diversity': score_diversity(references),
        'completeness': score_completeness(references)
    }
    
    return {
        'references': references,
        'scores': scores,
        'average_score': mean(scores.values()),
        'missing_papers': find_missing_papers(references),
        'suggestions': generate_citation_suggestions(scores)
    }
```

### Step 7: 综合评分与报告

```python
def generate_comprehensive_report(
    paper,
    citation_validation,
    gap_validation,
    hypothesis_assessment,
    method_assessment,
    citation_quality
):
    """生成综合审查报告"""
    
    # 加权评分
    weights = {
        'citation_validation': 0.30,
        'gap_validation': 0.20,
        'hypothesis_assessment': 0.20,
        'method_assessment': 0.20,
        'citation_quality': 0.10
    }
    
    overall_score = weighted_average(
        citation_validation, gap_validation, hypothesis_assessment,
        method_assessment, citation_quality, weights
    )
    
    # 确定推荐
    if overall_score >= 90:
        recommendation = 'ACCEPT'
    elif overall_score >= 75:
        recommendation = 'ACCEPT with minor revisions'
    elif overall_score >= 60:
        recommendation = 'MAJOR_REVISION'
    else:
        recommendation = 'REJECT'
    
    return {
        'overall_score': overall_score,
        'grade': score_to_grade(overall_score),
        'recommendation': recommendation,
        'sections': {
            'citation_validation': citation_validation,
            'gap_validation': gap_validation,
            'hypothesis_assessment': hypothesis_assessment,
            'method_assessment': method_assessment,
            'citation_quality': citation_quality
        },
        'critical_issues': find_critical_issues(paper, overall_score),
        'improvement_suggestions': generate_improvement_suggestions(
            paper, overall_score, recommendation
        )
    }
```

## 注意事项

### 1. 引用验证必须逐篇进行

- **不可偷懒**：每篇文献必须单独验证其引用理由
- **不可假设**：不可假设文献支持引用主张，必须实际阅读
- **不可模糊**：不可使用"大致正确"等模糊表述，必须精确引用

### 2. 研究空白验证必须独立

- **不可信任**：不可信任论文自己声称的空白，必须独立验证
- **不可遗漏**：必须检查所有可能的空白声明
- **不可遗漏竞争者**：必须检查相邻领域是否有竞争者填补了空白

### 3. 科学假设评估必须严格

- **可证伪性优先**：不可证伪的假设不评分
- **新颖性检查**：必须检查假设是否真正新颖
- **可行性评估**：必须评估假设的实验可行性

### 4. 解决方法评估必须客观

- **客观标准**：必须使用领域客观标准
- **SOTA对比**：必须与现有最佳方法对比
- **可复现性**：必须评估方法的可复现性

### 5. 文献引用质量必须全面

- **多维评分**：必须从5个维度（权威性、相关性、时效性、多样性、完整性）评分
- **缺失检测**：必须检测缺失的重要文献
- **建议补充**：必须提供具体的补充建议

## 参考文件

- `references/quality-standards.md` — 质量评分标准详细定义
- `references/citation-verification-guide.md` — 引用验证操作指南
- `references/gap-validation-guide.md` — 空白验证操作指南
- `references/hypothesis-assessment-guide.md` — 假设评估操作指南
- `references/method-assessment-guide.md` — 方法评估操作指南
- `references/citation-quality-guide.md` — 引用质量评分操作指南

## 脚本

- `scripts/deep_review.py` — 论文质量深度审查引擎主脚本
- `scripts/citation_validation.py` — 引用验证子脚本
- `scripts/gap_validation.py` — 空白验证子脚本
- `scripts/hypothesis_assessment.py` — 假设评估子脚本
- `scripts/method_assessment.py` — 方法评估子脚本
- `scripts/citation_quality.py` — 引用质量评分子脚本
