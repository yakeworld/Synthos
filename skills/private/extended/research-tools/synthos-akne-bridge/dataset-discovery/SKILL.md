---
name: dataset-discovery
description: '1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` p'
signature: 'dataset-discovery -> synthos-akne-bridge: synthetic skill for dataset discovery'
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
    description: '1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` p'
    signature: 'dataset-discovery -> synthos-akne-bridge: synthetic skill for dataset discovery'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 医学/健康数据集检索需求 — 领域关键词（如 stroke、breast cancer）
- **input**: OpenML API 查询参数 — limit/offset（limit=50 分页，避免 >200 截断 JSON）
- **output**: 候选数据集列表 — OpenML `data.dataset` 数组（did、名称、指标）
- **output**: 数据源可用性结论 — OpenML/UCI Archive 可得性判定与替代数据源指引

## 原则 (Principles)

> **分页而取，不贪多截。** OpenML `limit>200` 常致 JSON 截断，以 limit=50 + offset 分页为则，求全不贪多。
> **验物验文，不信状态码。** GitHub 镜像 404 仍返 HTTP 200——必验文件首行内容，状态码不可恃，文件内容为准。
> **源亡则明，合成备案。** 数据源俱 404 时，按已知 schema 以固定种子生成合成数据集，并明示其为合成，不冒真数据之实。

|
| **OpenML** | ✅ JSON API | N/A | No | `/api/v1/json/data/list` — response is `data.dataset` array, not `data.data`. `did` not `id`. No stroke datasets found. See `references/openml-api-behavior.md` for full details. |
| **UCI Archive** | ❌ Removed | ❌ | No | Healthcare Dataset (stroke) and Breast Cancer datasets removed from UCI. All mirrors dead. For alternatives see skill `healthcare-dataset-discovery`. |


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[DATA-001]** 调用 OpenML API 获取数据集列表时 → 必须使用 `limit=50` 配合 `offset` 进行分页，严禁单次请求 `limit > 200` 以防 JSON 截断
- **[DATA-002]** 解析 OpenML API 返回的质量指标数值时 → 必须将字符串类型（如 `"684.0"`）转换为 `float`，不可直接按整数或原生数值处理
- **[DATA-003]** 验证 GitHub 镜像或远程文件可用性时 → 必须检查文件首行内容（如 `head -1`）以识别 404 HTML 页面，不可仅依赖 HTTP 200 状态码
- **[DATA-004]** 在 OpenML 中执行数据集搜索时 → 必须使用 `/api/v1/json/data/list/` 接口进行过滤，避免使用无效的 `/tag/` 或 `/name/` 专用端点
- **[DATA-005]** 所有公开数据源（UCI/GitHub/HF等）均返回 404 或不可用时 → 依据已知 Schema 和统计特征生成固定种子的合成数据集，并明确标注其为合成数据
- **[DATA-006]** 解析 OpenML API 响应结构时 → 必须从 `data.dataset` 数组中提取数据，并使用 `did` 字段作为唯一标识符，而非 `data.data` 或 `id`

## OpenML Pitfalls

1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` pagination.
2. **Value types**: All quality metric values are **strings** (e.g., `"684.0"`), not numbers. Must use `float()` not `int()` conversion.
3. **Tag search**: `/api/v1/json/data/tag/{tag}` returns `{"error": "Function not valid"}` — tag queries use different endpoint.
4. **Name search**: `/api/v1/json/data/name/{name}` also returns error — search uses `/api/v1/json/data/list/` with filtering.
6. **GitHub fallback unreliable**: Many GitHub repos hosting "UCI datasets" return 404 on raw URLs. curl returns HTTP 200 for the 404 HTML page — always check file content (`head -1`), not just return code. If first line is "404: Not Found" or contains "html", the file doesn't exist.

## UCI Dataset Availability

The UCI Healthcare Dataset (healthcare-dataset-stroke-data.csv) is NOT available from any public source (UCI: 404, all GitHub mirrors: 404, HuggingFace: 404, Kaggle: auth-required). For alternatives, see skill `healthcare-dataset-discovery` (Cardiovascular-Disease-dataset, DID=45547, 70,000 records).
- `dsrscientist/dataset1/master/healthcare-dataset-stroke-data.csv` → 404
- `codeheroku/Stroke-Prediction/main/` → 404
- `srinivas/Stroke-Prediction/` → 404
- `krishnaik06/Stroke-Prediction/` → 404
- `anand8796/Stroke-prediction/` → 404
- `CodeWithEmil/UCI-Machine-Learning-Repository/main/healthcare/` → 404

The UCI repository moved to SPA at `archive.ics.uci.edu`. Direct file links (e.g., `.../00504/healthcare-dataset-stroke-data.csv`) return "NOT FOUND". The original dataset may have been removed or moved to a different URL.

**Workaround**: If no working download source exists, generate a synthetic dataset matching the known schema (12 features, 5179 rows, approximate statistics from UCI documentation). Use `random.seed(42)` for reproducibility. Document clearly that the dataset is synthetic and based on the UCI schema.

**2026-06-06 Update**: Exhaustive check across 5+ platforms confirmed UCI dataset is **completely gone**:
- UCI Archive: 404
- GitHub (all mirrors): All 404 (including GitHub Code Search returning 0 results)
- OpenML: 412 Precondition Failed (all endpoints blocked)
- HuggingFace Datasets: 404
- Kaggle: Auth required (no public download without OAuth)
- Google Dataset Search: No direct CSV link

## Reference Files

- `references/2026-06-05-dataset-discovery-lessons.md` — Crossref API quirks, PubMed endpoints, search patterns
- `references/uci-stroke-404-session-2026-06-05.md` — Complete 404 detection patterns for UCI datasets on GitHub

## Workflow: Find Medical Dataset

1. **OpenML** → list datasets with `limit=50/offset=0,50,100...`
2. Filter names against medical keywords
3. Cross-reference with existing papers (check `outputs/papers/` for duplicates)
4. Use OpenML data ID to fetch metadata and quality stats
5. For literature check: **Crossref** (paper metadata) → **Semantic Scholar** (more papers)
6. Download data from OpenML download URL

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
