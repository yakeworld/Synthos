---
name: dataset-discovery
description: "| Platform | REST API | Scraping | Auth Required | Notes |"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---





## IO_CONTRACT

- **input**: `domain: str, data_type: str` — 用户请求描述、上下文信息
- **output**: `datasets: list — 数据集发现`

> 对应原则：P2（机械原子暴露输入输出规范）



# Dataset Discovery

## Platform Access Matrix

| Platform | REST API | Scraping | Auth Required | Notes |
|----------|----------|----------|---------------|-------|
| **OpenML** | ✅ JSON API | N/A | No | `/api/v1/json/data/list` — response is `data.dataset` array, not `data.data`. `did` not `id`. No stroke datasets found. See `references/openml-api-behavior.md` for full details. |
| **UCI Archive** | ❌ Removed | ❌ | No | Healthcare Dataset (stroke) and Breast Cancer datasets removed from UCI. All mirrors dead. For alternatives see skill `healthcare-dataset-discovery`. |

## OpenML Pitfalls

1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` pagination.
2. **Value types**: All quality metric values are **strings** (e.g., `

  io_contract: input: ['search_query: str, platforms: list[str] -> dataset_results: list[Dataset]', 'output: ['dataset_results: list[Dataset] (name, platform, url, description, size, access_type, relevance)']


# Dataset Discovery

## Platform Access Matrix

| Platform | REST API | Scraping | Auth Required | Notes |
|----------|----------|----------|---------------|-------|
| **OpenML** | ✅ JSON API | N/A | No | `/api/v1/json/data/list` — response is `data.dataset` array, not `data.data`. `did` not `id`. No stroke datasets found. See `references/openml-api-behavior.md` for full details. |
| **UCI Archive** | ❌ Removed | ❌ | No | Healthcare Dataset (stroke) and Breast Cancer datasets removed from UCI. All mirrors dead. For alternatives see skill `healthcare-dataset-discovery`. |

## OpenML Pitfalls

1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` pagination.
2. **Value types**: All quality metric values are **strings** (e.g., `
metadata:
  synthos:
    priority: P2
    atom_type: tool
    description: Dataset discovery across platforms — OpenML, Kaggle, UCI, Crossref, Semantic Scholar.
    signature: 'search_query: str, platforms: list[str] -> dataset_results: list[Dataset]'
    related_skills: ["healthcare-dataset-discovery"]
---



# Dataset Discovery

## Platform Access Matrix

| Platform | REST API | Scraping | Auth Required | Notes |
|----------|----------|----------|---------------|-------|
| **OpenML** | ✅ JSON API | N/A | No | `/api/v1/json/data/list` — response is `data.dataset` array, not `data.data`. `did` not `id`. No stroke datasets found. See `references/openml-api-behavior.md` for full details. |
| **UCI Archive** | ❌ Removed | ❌ | No | Healthcare Dataset (stroke) and Breast Cancer datasets removed from UCI. All mirrors dead. For alternatives see skill `healthcare-dataset-discovery`. |

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
