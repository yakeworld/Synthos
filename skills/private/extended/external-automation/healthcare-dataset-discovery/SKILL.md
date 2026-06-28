---

name: healthcare-dataset-discovery
description: 'Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.'
author: Synthos
license: MIT
version: 1.0.0
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
metadata:
  synthos:
    priority: P2
    atom_type: tool
    description: Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.
    signature: "medical_domain: str -> dataset_results: list[Dataset] -> dataset_results: list[Dataset] (name, source, url, description, access_type, relevance)"
    related_skills: []


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




# Healthcare Dataset Discovery

## Discovery Protocol

When searching for public healthcare datasets:

1. **OpenML** → Primary source. Use `/api/v1/json/data/list` (not `/limit/50` pattern). Response structure: `{"data": {"dataset": [...]}}` with `did`, `NumberOfInstances`, `NumberOfFeatures` fields.
2. **HuggingFace** → `/datasets-server.huggingface.co/search?query={keyword}&limit=50` (returns 422 on this server — may need alternate access)
3. **Kaggle** → Requires authentication. Check `/datasets?search={keyword}` but expect paywalls.
4. **UCI Archive** → Many datasets removed. Check `archive.ics.uci.edu` — expect 404 for popular datasets.

## Known Dataset Status

### ✅ ACCESSIBLE
- **OpenML Cardiovascular-Disease-dataset** (DID=45547): 70,000 records, 13 features, 50/50 CVD class balance. Features: age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, cardio. Download via `https://www.openml.org/data/v1/download/{file_id}`.

### ❌ UNAVAILABLE
- **UCI Healthcare Dataset** (healthcare-dataset-stroke-data.csv): Removed from UCI. All GitHub mirrors dead (dsrscientist, codeheroku, krishnaik06, etc.). HuggingFace: 404. Kaggle: requires auth.
- **UCI Breast Cancer** (WDBC): Also moved/removed from UCI.

## API Quirks

- OpenML `list` endpoint returns 6,400+ datasets. Search locally by name/description.
- OpenML detail API returns `{"data_set_description": {...}}` (NOT `{"data": {"dataset": {...}}}`).
- OpenML `limit/5` works but `limit/500` returns empty — use `/api/v1/json/data/list` without limit.
- Crossref `query=` param works (not `search=`). Use `+` for spaces or `quote_plus()`.
- PubMed eSearch requires `+` for spaces, not URL encoding.

## Reference

- See `references/uci-stroke-404-session.md` for detailed investigation transcript

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
