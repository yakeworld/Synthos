# 使用 Semantic Scholar 进行专利查新（降级查新）

当 CNIPA 公布公告检索工具不可用时（Playwright浏览器依赖故障、网络限制等），可使用 Semantic Scholar API 作为降级方案进行专利查新。**不能替代 CNIPA 官方检索**，但可快速确认学术文献层面的新颖性。

## API 查询示例

```bash
# 基础查询——Kappa角标定
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=kappa+angle+calibration+3D+gaze&limit=10&fields=title,publicationDate,externalIds,abstract,venue" \
  -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY"

# 查询特定方法组合（验证组合新颖性）
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=vestibulo-ocular+reflex+eye+tracking+calibration&limit=10&fields=title,publicationDate,externalIds" \
  -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY"
```

## 最佳实践

### 1. 分层查新策略

| 层级 | 查询方向 | 用途 |
|:-----|:---------|:-----|
| L1 | 核心技术词 | 确认本领域现有方法（如 `kappa angle calibration`） |
| L2 | 方法+创新要素组合 | 验证组合新颖性（如 `kappa angle VOR calibration`） |
| L3 | 完整技术方案 | 确认整体方案未公开（如 `VOR eye tracking calibration patent`） |

### 2. 新颖性判断标准

| 语意搜索返回结果 | 判定 | 示例 |
|:----------------|:-----|:-----|
| 核心词返回≥20篇，但**方法组合词返回0篇** | ✅ **组合新颖性确认** | `kappa angle calibration`=65篇, 不含`VOR`=0篇 |
| 方法组合词返回1-2篇 | ⚠️ 需要阅读全文确认差异化 | 注意区分：相关≠相同 |
| 方法组合词返回≥3篇直接相关文献 | ❌ 新颖性存疑，需重新定位创新点 | 建议调整专利点方向 |

### 3. 字段选择

专利查新建议选择以下字段（`&fields=`参数）：

```
title,publicationDate,externalIds,abstract,venue,authors
```

- `externalIds` — 包含DOI和ArXiv ID，可进一步获取全文
- `abstract` — 用于摘要级差异化判断（300字内的技术摘要）
- `publicationDate` — 按年份排序，优先查看最新文献

### 4. 局限性

| 局限 | 应对 |
|:-----|:-----|
| 不含专利全文（仅学术论文） | 结合Google Patents搜索（用 `field:patent` 或浏览器打开） |
| 429限流 | 加 `sleep(1)` 间隔；短查询组合（如"VOR+calibration"）可能被500拒绝，尝试换词 |
| 无中文专利数据 | 中文专利必须用CNIPA正式检索 |
| Semantic Scholar结果不全 | 可再查PubMed（`pubmed` skill）、Google Scholar补充 |
