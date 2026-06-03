# Research Agent Competition & Benchmark Landscape

Discovered 2026-05-12 during Synthos external absorption cycle. Updated when new benchmarks emerge.

## Active Benchmarks

### ResearchRubrics (ICLR 2026)
| Dimension | Detail |
|:----------|:-------|
| **Provider** | ScaleAI |
| **Stars** | ⭐20 |
| **Evaluate** | Deep Research Agent research report quality against structured rubrics |
| **Dataset** | HuggingFace `ScaleAI/researchrubrics` (processed_data.jsonl) |
| **Format** | Submit `.md` reports → LLM (Gemini 2.5 Pro) scores against rubric criteria |
| **Scoring** | Compliance score per rubric criterion, weighted aggregation |
| **Code** | `github.com/scaleapi/researchrubrics` |
| **Best for Synthos** | ARG atom directly maps to report generation; HYP + ASC for prior pipeline stages |
| **Setup** | LiteLLM API key → pip install → download dataset → run `evaluate_reports_batch.py` |
| **Synthos test (2026-05-12)** | 3/101 tasks run: AI Drug Discovery (4,594 words, 22 rubrics), NELF-E HCC (2,482 words, 26 rubrics), Engram-PC (3,960 words, 22 rubrics). All pipeline steps (ACQ→KEX→ASC→HYP→ARG) executed successfully. Formal scoring needs Gemini 2.5 Pro (DeepSeek-as-judge gave unreliable results). |
| **Lesson** | Synthos is strong on research synthesis but needs rubric alignment (exact section headers, word count, DOI format). This is a format-level issue, not a capability issue. Use `HF_ENDPOINT=https://hf-mirror.com` when downloading from China. |

### BrowseComp-Plus (ACL 2026)
| Dimension | Detail |
|:----------|:-------|
| **Provider** | Tevatron |
| **Stars** | ⭐265 |
| **Evaluate** | Deep-Research agent search + reasoning on fixed corpus (~100K documents) |
| **Dataset** | HuggingFace `Tevatron/browsecomp-plus` |
| **Leaderboard** | HuggingFace space |
| **Format** | Agent receives query → searches fixed corpus → produces answer |
| **Scoring** | Token F1, tool call counts, status |
| **Code** | `github.com/texttron/BrowseComp-Plus` |
| **Best for Synthos** | ACQ + KEX + ASC pipeline (search + extract + relate) |
| **Setup** | Python 3.10 + Java 21 + `uv sync` → download indexes → run agent |

### HeurekaBench (ICLR 2026)
| Dimension | Detail |
|:----------|:-------|
| **Provider** | MLBio @ EPFL |
| **Stars** | ⭐11 |
| **Evaluate** | AI Co-Scientist on single-cell data analysis |
| **Dataset** | 44GB scRNA-seq data (Google Drive) |
| **Format** | Agent receives question + data → produces analysis answer |
| **Scoring** | Multiple choice + open-ended, verified against published findings |
| **Code** | `github.com/mlbio-epfl/HeurekaBench` |
| **Best for Synthos** | Full 6-atom pipeline on biomedical data |
| **Setup** | pip install → 44GB data download → configure LLM agent |

### AIS 2024 Event-Based Eye Tracking Challenge (CVPR 2024)
| Dimension | Detail |
|:----------|:-------|
| **Evaluate** | Event camera eye tracking — pupil center prediction |
| **Relevance** | Directly related to user's 3D head-mounted ET grant |
| **Data** | Event-based eye movement recordings |
| **Status** | Past (2024), but survey paper has 30+ cites — methodology reference |

## Triage Rules

When the user asks to "evaluate" or "test" Synthos:

1. **If they want quick validation**: Search `research-paper-search` steps + do manual rubric check against ResearchRubrics criteria — no dataset download needed
2. **If they want benchmark score**: Pick one benchmark based on which atom they want to validate:
   - **ACQ/KEX**: BrowseComp-Plus (needs Java + Python setup)
   - **ARG**: ResearchRubrics (simplest setup, LiteLLM key only)
   - **Full pipeline**: HeurekaBench (heaviest, needs 44GB data)
3. **Never propose all three at once** — each has different setup requirements and time commitment

## Infrastructure Requirements

| Benchmark | Key | Storage | Python | Other |
|:----------|:---:|:-------:|:------:|:------|
| ResearchRubrics | LiteLLM | 10MB | 3.8+ | — |
| BrowseComp-Plus | — | 1-5GB | 3.10 | Java 21 |
| HeurekaBench | — | 44GB+ | 3.12 | Conda |
