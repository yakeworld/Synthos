---
name: dataset-discovery
description: '1. **Pagination limit**: `limit > 200` often produces truncated JSON.
  Use `limit=50` with `offset` p'
signature: 'dataset-discovery -> synthos-akne-bridge: synthetic skill for dataset
  discovery'
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
    description: '1. **Pagination limit**: `limit > 200` often produces truncated
      JSON. Use `limit=50` with `offset` p'
    signature: 'dataset-discovery -> synthos-akne-bridge: synthetic skill for dataset
      discovery'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
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

- [ ] OpenML 请求使用 `limit=50` 配合 `offset` 分页，单次请求未超过 `limit>200`（防 JSON 截断）
- [ ] 质量指标数值已从字符串转为 `float`（如 `"684.0"` → 684.0），未直接按 int 或原生数值处理
- [ ] 远程文件（GitHub 镜像等）通过 `head -1` 检查首行内容确认真实存在，未仅依赖 HTTP 200 状态码
- [ ] OpenML 搜索使用 `/api/v1/json/data/list/` 过滤端点，未调用无效的 `/tag/` 或 `/name/` 端点
- [ ] 响应数据从 `data.dataset` 数组提取，以 `did` 字段为唯一标识，未误用 `data.data` 或 `id`
- [ ] 数据源均 404 时，合成数据集基于已知 schema 与固定种子 `random.seed(42)` 生成，并明确标注为合成数据
- [ ] 候选数据集已与 `outputs/papers/` 现有论文交叉核对，排除重复

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 医学关键词 "breast cancer" + OpenML 查询参数 `limit=50, offset=0`（Workflow 第 1-2 步 / 示例 1）
- **Golden Output**: 响应 JSON 无截断，从 `data.dataset` 数组按 `did` 提取候选数据集，质量指标以 `float()` 转换（如 `"684.0"` → 684.0），并与 `outputs/papers/` 交叉去重
- **Golden Error**: UCI stroke 数据集全源 404（UCI/GitHub 镜像/HF/Kaggle 均确认失效）时 → 按 DATA-005 报错提示数据源不可用，并给出恢复建议：以 `random.seed(42)` 按已知 schema（12 特征, 5179 行）生成合成数据集且明示合成身份；镜像验证报错须以 `head -1` 首行内容（"404: Not Found"/html）为准，不得仅凭 HTTP 200 判定

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## 示例 · EXAMPLES

**示例 1 · OpenML 分页检索（Workflow 第 1-2 步）**
- 输入：医学关键词 "breast cancer" + OpenML 查询参数
- 操作/输出：`/api/v1/json/data/list/` 按 `limit=50, offset=0/50/100...` 分页（DATA-001/004），从 `data.dataset` 取 `did`（DATA-006），过滤出候选数据集
- 验证：JSON 无截断、无 `limit>200` 请求，响应按 `data.dataset`/`did` 解析成功

**示例 2 · 字符串指标与 GitHub 镜像核验（Pitfalls 2/6）**
- 输入：候选数据集的质量指标 `"684.0"` + 某 GitHub 镜像 raw URL
- 操作/输出：`float("684.0")` 转换（DATA-002）；对 URL `curl` 后 `head -1` 查首行（DATA-003），发现首行含 "404: Not Found"/"html" 即判定镜像失效，不凭 HTTP 200
- 验证：指标为 float 类型；首行内容判定与状态码结论一致，通过"验物验文，不信状态码"原则

**示例 3 · 源亡则合成（Workaround / DATA-005）**
- 输入：UCI stroke 数据集全源 404（UCI/GitHub 镜像/HF/Kaggle 均已确认失效）
- 操作/输出：按已知 schema（12 特征, 5179 行）以 `random.seed(42)` 生成合成数据集并明确标注"合成，基于 UCI schema"
- 验证：固定种子可复现（P1 原子可复现性），文档明示合成身份，未冒真数据之实
