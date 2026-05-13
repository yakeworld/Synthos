# Citation Verification — 引用验证流程

> 吸收自 AutoResearchClaw `literature/verify.py` + ARS (Academic Research Skills) 5-type hallucination taxonomy
> 对应原则：P0（证据可溯性）

## 引用幻觉5分类法（[ARS吸收] 自 Academic Research Skills v3.7）

基于 GPTZero × NeurIPS 2025 (Adams et al., 2026) 研究，**每篇论文验证时必须检测这5种模式**：

| 类型 | 编码 | 频率 | 描述 | 检测策略 |
|------|------|------|------|---------|
| **完全编造** | TF | ~28% | 整篇论文不存在——标题作者期刊全部编造 | WebSearch 标题+作者；无结果→TF |
| **假作者/会议** | PAC | ~23% | 真实学者被归到没写过的论文 | 查该作者的Google Scholar真实发文列表 |
| **不完整幻觉** | IH | ~19% | 缺少可验证细节（无DOI、模糊页码、无卷号） | 标记无DOI+卷+页码的论文为深查对象 |
| **部分幻觉** | PH | ~18% | 不同来源的真实元素混搭（如真实标题+假作者） | 所有元数据对**单一来源**交叉验证 |
| **微妙幻觉** | SH | ~12% | 小扭曲（错年份、扩写缩写、换期刊） | 逐字段对比出版商页面 |

**5种复合欺骗模式**（76%的TF案例）：
1. **作者伪装** (PAC+TF): 编造的论文归到真实活跃研究者名下
2. **期刊利用** (PH+PAC): 真实期刊名 + 假文章细节
3. **混合编造** (PH): 2-3篇真实论文的元素混合成一篇假论文
4. **时间掩饰** (SH): 正确作者+话题 + 错误年份
5. **DOI误导**: 假DOI指向真实但不相关的论文（64%的假DOI案例）

**核心规则**：
- "难以验证"**不是**有效判决 — 灰色地带 = FAIL
- 每条引用必须达到 VERIFIED / NOT_FOUND / MISMATCH 之一
- 100% WebSearch 审计轨迹（搜索查询、顶部结果URL、确认的具体书目信息）
- 书籍章节需要增强验证（查TOC/DOI确认具体章节）

## 概述

knowledge-acquisition 原子从 API 检索论文后，Agent 需要对每篇引用的论文进行验证，
确保引用真实存在、元数据准确、与研究主题相关。

## 4层验证策略

### L1: DOI 验证（最快）

```
curl -s -o /dev/null -w "%{http_code}" "https://api.crossref.org/works/{DOI}"
→ 200 = DOI 有效
→ 404 = DOI 不存在
```

如果论文有 DOI，直接验证。DOI 是最高置信度的标识符。

### L2: arXiv ID 验证

```
curl -s "http://export.arxiv.org/api/query?id_list={arxiv_id}" | grep -c "<id>"
→ ≥1 = arXiv ID 有效
→ 0 = arXiv ID 不存在
```

仅当论文有 arxiv_id 时执行。

### L3: Semantic Scholar 交叉搜索

```
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_title}&limit=3&fields=title,year,doi" \
  -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY"
```

取前3个结果，计算与目标论文的标题相似度：
- 最高相似度 ≥ 0.80 → VERIFIED
- 0.50 ≤ 最高 < 0.80 → SUSPICIOUS
- < 0.50 → HALLUCINATED

### L4: LLM 相关性评分（仅对验证通过的论文）

Agent 阅读论文标题+摘要，判断是否与研究主题相关：
- 相关性 > 0.7 → RELEVANT
- 0.4-0.7 → MARGINAL
- < 0.4 → IRRELEVANT

## 输出格式

每篇论文在 `raw_papers` 数组中的引用验证结果：

```json
{
  "title": "论文标题",
  "doi": "10.xxxx/xxxxx",
  "year": 2024,
  "source": "semantic_scholar",
  "citation_verification": {
    "status": "verified|suspicious|hallucinated|skipped",
    "confidence": 0.95,
    "methods_used": ["doi", "title_search"],
    "integrity_score": 0.95,
    "relevance_score": 0.85,
    "details": "DOI resolved via Crossref. Title match confirmed via S2."
  }
}
```

## 评分标准

| 状态 | 条件 | 行为 |
|------|------|------|
| VERIFIED | L3 验证通过 (sim ≥ 0.80) | 正常加入输出 |
| SUSPICIOUS | L3 partial (0.50 ≤ sim < 0.80) | 标记，由 Agent 判断是否保留 |
| HALLUCINATED | 所有层都失败 (sim < 0.50) | 从输出中排除，记录到 evidence |
| SKIPPED | 无标题或 API 不可达 | 保留但标记为未验证 |

## 集成到 knowledge-acquisition 流程

在 skill_view('knowledge-acquisition') 加载后的执行流程中，在"API 检索"步骤之后增加"引用验证"步骤：

```
1. 用户查询 → 确定关键词
2. 多源检索 (S2 + PubMed + OpenAlex)  →  现有步骤
3. [新增] 去重合并论文列表
4. [新增] 对每篇论文执行4层引用验证
5. [新增] 过滤掉 HALLUCINATED 的论文
6. [新增] 标记关联论文的 relevance_score
7. 返回验证后的论文列表 + 下载PDF
8. 保存到 <run_dir>/knowledge-acquisition_output.json
```

## 参考

- AutoResearchClaw `researchclaw/literature/verify.py` — 4层验证架构
- CrossRef API: https://api.crossref.org/works/{doi}
- arXiv API: http://export.arxiv.org/api/query?id_list={id}
- Semantic Scholar API: https://api.semanticscholar.org/graph/v1/paper/search
