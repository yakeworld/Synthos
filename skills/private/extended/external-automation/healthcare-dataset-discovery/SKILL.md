---
name: healthcare-dataset-discovery
description: 1. 确认输入参数完整
signature: 'healthcare-dataset-discovery -> external-automation: synthetic skill for
  healthcare dataset discovery'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 确认输入参数完整
    signature: 'healthcare-dataset-discovery -> external-automation: synthetic skill
      for healthcare dataset discovery'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
category: research
signature: "healthcare-dataset-discovery -> research: 'Public healthcare dataset discovery — known accessible sources, dead sources, a"
related_skills: ['dataset-discovery', 'openml-benchmark']
description: 'Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.'
author: Synthos
license: MIT
version: 1.0.0

    atom_type: tool
    description: Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.
    signature: "medical_domain: str -> dataset_results: list[Dataset] -> dataset_results: list[Dataset] (name, source, url, description, access_type, relevance)"
    related_skills: []
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
## Golden 集合 · GOLDEN SET
- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[HEAL-001]** 当需要获取 OpenML 数据集列表时 → 使用 `/api/v1/json/data/list` 端点获取全量数据并在本地过滤，避免使用 `limit/500` 等可能导致空结果的参数
- **[HEAL-002]** 当解析 OpenML API 响应时 → 区分列表接口（`{"data": {"dataset": [...]}}`）与详情接口（`{"data_set_description": {...}}`）的不同 JSON 结构
- **[HEAL-003]** 当搜索 UCI Archive 中的经典医疗数据集时 → 预期大量数据集已移除或返回 404，需优先验证 GitHub 镜像或 HuggingFace 的可用性
- **[HEAL-004]** 当调用 Crossref 或 PubMed API 进行文献/数据检索时 → 使用 `+` 符号或 `quote_plus()` 处理空格，而非标准 URL 编码，以确保查询参数正确解析
- **[HEAL-005]** 当评估数据集来源的可靠性时 → 优先选择 OpenML 等提供稳定 API 和明确元数据（如 DID、特征数）的来源，规避需要认证或存在付费墙的平台（如 Kaggle）
- **[HEAL-006]** 当执行数据集发现任务时 → 首先确认输入参数完整性，并在执行核心操作前验证目标源点的可达性（如检查已知死链）