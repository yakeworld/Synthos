# Paper Pipeline P-1 → Grant Proposal Adaptation

> Bridges the paper-pipeline's P-1 (ACQ→EXT→ASC→GAP→HYP) workflow to grant proposal reconstruction.
> Created: 2026-05-25 (RFID hospital asset management proposal session)

## Why This Adaptation

paper-pipeline's P-1 was designed for academic paper writing. Grant proposals differ:

| Dimension | Academic Paper | Grant Proposal |
|:----------|:--------------|:---------------|
| Audience | Peer reviewers | Administrative + domain experts |
| Evidence depth | Deep, single question | Broad, multi-dimensional |
| Innovation bar | Novel finding | Engineering/management innovation acceptable |
| Budget constraint | Not applicable | Dictates feasibility (市局1-5万≠面上50万) |
| Timeline | Open-ended | Fixed 12-36 months |
| References | 30-50 | 8-15 (Chinese format) |

## Adapted P0 Workflow

### Step 1: ACQ — Literature Search (NotebookLM Deep Research)

Target 3-4 parallel searches covering:
- Core technology (e.g., "UHF RFID hospital asset tracking")
- Application cases (e.g., "RTLS healthcare implementation case study")
- Chinese language (e.g., "医院 资产管理 RFID 业财融合")
- Supplementary domain (e.g., "IoMT security healthcare IoT")

**Grant-specific filter**: Prefer case studies and implementation reports (not basic science). Vendors' white papers are acceptable as supporting evidence — grants value practical feasibility.

### Step 2: EXT + ASC — Knowledge Extraction & Association

Ask Gemini to identify:
- Common technology bottlenecks (e.g., metal/water interference in hospitals)
- Organizational barriers (e.g., equipment hoarding behavior)
- Integration gaps (e.g., RTLS → ERP data flow)

**Grant-specific filter**: Focus on problems that can be solved within 12 months with 1-5万 budget.

### Step 3: GAP — Formal Gap Statement

Format:
- (1) Known: What has been demonstrated
- (2) Unknown: What specifically hasn't been tried/systematically evaluated
- (3) Value: What filling this gap enables

### Step 4: HYP — Hypothesis Formation

Generate 3 hypotheses and evaluate each against budget/time:

| Hypothesis | Budget Needs | Timeline | Verdict for 市局项目 |
|:-----------|:-------------|:---------|:-------------------|
| H₁: High-precision multi-sensor fusion | Hardware-intensive (5万+) | 12-18 months | ❌ Too expensive |
| H₂: Hospital-led process redesign | Personnel + training | 18+ months | ❌ Too slow |
| H₃: API-based business-finance integration | Software-only (1-3万) | 6-12 months | ✅ **Best fit** |

### Step 5: Proposal Reconstruction

Only after H₃ is confirmed, open the template document. The hypothesis drives the entire content structure:
- Background: frames the gap
- Content: operationalizes the hypothesis
- Methods: describes verification design
- Targets: quantifies the hypothesis's success criteria

## Pitfalls

1. **Don't look at the template first.** The existing document will bias your thinking toward its framing. Do P0 completely before opening the .doc.
2. **Don't downgrade hypotheses to fit budget.** Generate the ideal hypothesis first, then filter by budget — not the reverse. You might discover an affordable version of H₁.
3. **Don't ignore industry sources.** Grant reviewers at municipal level value practical case studies (vendor white papers, hospital pilot reports) as much as academic papers.
4. **Don't skip the falsification condition.** Grants without clear "what failure looks like" are hard to evaluate. The falsification condition IS your validation plan.
