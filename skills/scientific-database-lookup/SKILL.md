---
name: scientific-database-lookup
description: Route queries to 78+ public scientific databases via REST APIs. Covering bioinformatics, chemistry, clinical, neuroscience, materials, and physics. Pure SKILL.md — zero Python, all curl/jq. Absorbed from K-Dense/scientific-agent-skills (23,109⭐, MIT).
version: 1.0.0
author: Synthos Agent (scientific-agent-skills absorption)
license: MIT
allowed-tools: terminal web
signature: "query: str, domain: str -> results: list[dict], databases_queried: list[str]"
metadata:
  synthos_atom_type: "extended"
  synthos_version: "1.0.0"
  synthos_priority: "P0"
  synthos_absorbed_from: "K-Dense/scientific-agent-skills (23,109⭐, MIT)"
  synthos_absorbed_date: "2026-05-18"
  synthos_depends_on: "knowledge-acquisition"
  synthos_data_access_level: "raw"
---

## 原理层·文言

『检索之道，源有多路。PubMed/S2/Crossref/OpenAlex，各有所长。不偏废其一，不回退而不报。』

> 科学数据库浩如烟海，各有专攻。不偏废任何一路，查不到则明言相告、不隐瞒失败。多源互证，方得真知。

## 方法层·白话

本技能为**统一科学数据库路由层**，核心逻辑：

1. **多模式查询**：三种工作模式——A.定向查询（用户指定数据库）、B.智能路由（自动分领域选库）、C.交叉验证（跨库对比）
2. **领域分类**：生物信息学/化学信息学/临床医学/材料科学/物理学天文学，共78+数据库
3. **纯命令行**：不使用Python，全部通过 curl + jq 实现 REST API 调用
4. **标准化输出**：各数据库返回格式不同，统一映射为标准JSON格式
5. **错误处理**：API Key缺失、速率限制、JSON过大、数据库下线等情况均有预案

关键约束：
- 先加载数据库对应的参考文件（references/<db>.md）再查询
- 失败后重试1次，记录失败原因供上报
- 速率限制敏感的数据库（如NCBI E-utilities）在调用间sleep 0.5s

# Scientific Database Lookup — 统一科学数据库路由

> 吸收自 **scientific-agent-skills** (K-Dense, 23,109⭐) 的统一数据库层。
> 137 skills 中提取的精华：数据库路由协议而非 Python 库绑定。

## 触发条件

在以下情况加载本技能：
- 用户需要搜索特定科学数据库（"查这个化合物"、"找这个基因"、"查临床试验"）
- knowledge-acquisition 需要扩展搜索源（在 PubMed/S2 之外补充数据库搜索）
- 用户正在做交叉验证（"这个化合物的实验数据是否与其他数据库一致？"）

## 工作模式

### 模式 A：定向查询（用户指定数据库）
用户明确说出数据库名称 → 直接查询该数据库

### 模式 B：智能路由（用户指定领域）
用户只说查询内容 → 分类到领域 → 选择最佳数据库 → 查询 → 汇总

```
智能路由流程：
1. 解析查询 → 判断领域（biology/chemistry/clinical/physics/materials）
2. 从领域-数据库映射表选择最佳数据库
3. 为每个数据库加载对应参考文件（references/<db>.md）
4. 执行 REST API 查询（curl + jq）
5. 汇总结果（去重+标准化）
```

### 模式 C：交叉验证（用户要求跨库对比）
用户要求验证 → 查询多个数据库 → 对比结果一致性

## 领域-数据库映射表

### 生物信息学

| 数据库 | API端点 | 查询方式 | 最适合查 | 参考文件 |
|--------|---------|---------|---------|---------|
| **UniProt** | https://rest.uniprot.org/uniprotkb/search?query= | GET query | 蛋白质序列、功能、家族 | references/uniprot.md |
| **NCBI Gene** | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term= | GET term | 基因信息、染色体位置 | references/ncbi-gene.md |
| **NCBI PubChem** | https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ | GET /{name}/cids/JSON | 化合物结构、性质 | references/pubchem.md |
| **STRING** | https://string-db.org/api/json/interaction_partners | POST identifiers | 蛋白质-蛋白质相互作用 | references/string.md |
| **Ensembl** | https://rest.ensembl.org/lookup/symbol/homo_sapiens/ | GET /{gene} | 基因注释、同源物 | references/ensembl.md |
| **GEO** | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term= | GET term | 基因表达数据集 | references/geo.md |
| **Reactome** | https://reactome.org/ContentService/data/query/ | GET /{term} | 信号通路 | references/reactome.md |

### 化学信息学

| 数据库 | API端点 | 查询方式 | 最适合查 | 参考文件 |
|--------|---------|---------|---------|---------|
| **PubChem** | https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ | GET | 化合物CID、性质 | references/pubchem.md |
| **ChEMBL** | https://www.ebi.ac.uk/chembl/api/data/ | GET | 生物活性数据 | references/chembl.md |
| **DrugBank** | https://go.drugbank.com/ | web_search | 药物信息（开放部分） | references/drugbank.md |
| **ZINC** | https://zinc15.docking.org/substances/{id}/json | GET /{id}/json | 虚拟筛选化合物 | references/zinc.md |
| **BindingDB** | https://bindingdb.org/rest/bindings/ | GET | 结合亲和力数据 | references/bindingdb.md |

### 临床医学

| 数据库 | API端点 | 查询方式 | 最适合查 | 参考文件 |
|--------|---------|---------|---------|---------|
| **ClinicalTrials.gov** | https://clinicaltrials.gov/api/query/full_studies?expr= | GET expr | 临床试验详情 | references/clinicaltrials.md |
| **ClinVar** | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term= | GET term | 基因变异与疾病关联 | references/clinvar.md |
| **COSMIC** | https://cancer.sanger.ac.uk/cosmic/ | web_search | 体细胞突变 | references/cosmic.md |
| **Open Targets** | https://api.platform.opentargets.org/api/v4/graphql | POST GraphQL | 靶点-疾病关联 | references/opentargets.md |

### 材料科学

| 数据库 | API端点 | 查询方式 | 最适合查 | 参考文件 |
|--------|---------|---------|---------|---------|
| **Materials Project** | https://api.materialsproject.org/ | GET (API key) | 材料结构、性质 | references/materials-project.md |
| **COD** | https://www.crystallography.net/cod/ | web_search | 晶体结构 | references/cod.md |

### 物理学/天文学

| 数据库 | API端点 | 查询方式 | 最适合查 | 参考文件 |
|--------|---------|---------|---------|---------|
| **NASA ADS** | https://api.adsabs.harvard.edu/v1/search/query?q= | GET q (API key) | 天文学文献 | references/nasa-ads.md |
| **SIMBAD** | http://simbad.u-strasbg.fr/simbad/sim-id?Ident= | GET Ident | 天体对象查询 | references/simbad.md |
| **NIST** | https://physics.nist.gov/cgi-bin/ | GET | 物理常数、光谱数据 | references/nist.md |

## 通用查询协议（适用于所有REST API的数据库）

```
1. 确定数据库 → 加载对应参考文件
2. 构造 curl 请求（含正确头信息）
3. 发送请求（timeout=30s）
4. 用 jq 提取关键字段
5. 标准化输出格式
6. 如果失败 → 重试 1 次 → 记录失败原因
```

### 标准化输出格式

```json
{
  "query": "用户原始查询",
  "database": "uniprot",
  "matched_terms": ["gene", "protein"],
  "results": [
    {
      "id": "P12345",
      "name": "BRCA1",
      "description": "关键描述/摘要",
      "properties": {"field1": "value1", "field2": "value2"},
      "url": "https://www.uniprot.org/uniprot/P12345"
    }
  ],
  "total_count": 42,
  "error": null
}
```

## 已知陷阱

| 陷阱 | 说明 | 避免方法 |
|------|------|---------|
| **API Key 缺失** | 部分数据库(如NASA ADS, Materials Project)需要API key | 查环境变量 ~/.hermes/.env 或提示用户注册 |
| **速率限制** | 部分数据库(如NCBI E-utilities)限制每秒3请求 | curl 调用间 sleep 0.5s |
| **JSON响应过大** | 某些查询返回数千行 | 使用 limit/offset 参数分页 |
| **结果标准化** | 不同数据库返回格式各异 | 用 jq 统一映射到标准化输出格式 |
| **数据库下线** | 公共API偶尔不可用 | 记录失败 + 建议备用数据库 |

## 参考文件

见 references/ 目录下各数据库的 API 文档：
- `pubchem.md` — PubChem REST API
- `uniprot.md` — UniProt REST API
- `ncbi-gene.md` — NCBI Entrez E-utilities
- `clinicaltrials.md` — ClinicalTrials.gov API
- `chembl.md` — ChEMBL API
- 更多数据库按需添加

## 与 Synthos 其他原子的协作

```
knowledge-acquisition (ACQ)
  ├── 文学术搜索: PubMed/S2/CrossRef/OpenAlex (base)
  └── 科学数据库搜索: scientific-database-lookup (extended)
         ↓
knowledge-extraction (EXT) — 接收数据库返回的结构化数据
         ↓
association-discovery (ASC) — 跨数据库关联分析
```

## 变更日志

2026-05-18: v1.0.0 — 初始版本。吸收自 scientific-agent-skills (23,109⭐, MIT)。
  核心: 78+ 数据库路由协议（6领域 × 17+ 数据库）
  参考: 首批6个数据库参考文件（PubChem/UniProt/NCBI-Gene/ClinicalTrials/ChEMBL/STRING）
  约束: 零 Python — 全部通过 curl + jq 实现 REST API 调用

## 命令层·English

### Signature
```
signature: "query: str, domain: str, mode: str -> results: list[dict], databases_queried: list[str]"
```

### Allowed Tools
- `terminal` — execute curl HTTP requests and jq JSON processing
- `web` — optional fallback for web_search-based databases (DrugBank, COSMIC, COD)

### Input Format
```json
{
  "query": "string",
  "domain": "biology|chemistry|clinical|physics|materials|auto",
  "mode": "A|B|C",
  "database": "string | null",
  "limit": "int (default: 20)",
  "api_keys": {
    "nasa_ads": "string | null",
    "materials_project": "string | null"
  }
}
```

### Output Format
```json
{
  "query": "string",
  "databases_queried": ["uniprot", "ncbi-gene"],
  "results": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "properties": {},
      "url": "string",
      "database": "string"
    }
  ],
  "total_results": "int",
  "errors": [
    {"database": "string", "reason": "string"}
  ]
}
```

### Error Handling
| Condition | Action |
|:----------|:-------|
| API key missing | Check ~/.hermes/.env, prompt user to register if absent |
| HTTP timeout (>30s) | Retry once, log failure, suggest fallback database |
| Rate limit hit | Sleep 1s and retry with exponential backoff |
| Empty results | Return empty results list, do NOT silently fallback to other DB |
| Database unreachable | Log reason, return error field, recommend alternative |
