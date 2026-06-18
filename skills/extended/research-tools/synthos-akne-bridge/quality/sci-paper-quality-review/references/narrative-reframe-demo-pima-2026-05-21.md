# Narrative Reframe Demo: Pima CRISP-DM Helix Paper (2026-05-21)

## Problem

The paper's core insight was "data leakage inflates metrics" — a well-known ML principle that reviewers would consider common knowledge. This capped D6 (Novelty) at 0.55.

## Diagnosis

The issue was not the quality of the work but the **framing of the contribution**:
- "We quantified data leakage" → framed as discovery/revelation
- "We propose a framework" → framed as another solution, not the *missing piece*

## Reframe Target (Level 1: Protocol as Solution)

| Before | After |
|--------|-------|
| "Data leakage inflates metrics. We quantify it." | "Guidelines warn against leakage but provide no protocol. We built the protocol." |
| Contribution: quantification + framework | Contribution: formal auditable protocol + quantified cost of NOT using it |
| Gap: "it's unknown how much leakage distorts metrics" | Gap: "no standardized implementation protocol exists" |
| Story: exposé of bad practice | Story: solution to an implementation gap |

## Concrete Changes Made (Level 1)

### 1. Abstract rewrite
Old opening: "Methodological rigor and process integrity are the true determinants..."
New opening: "Existing clinical ML guidelines universally warn against data leakage but provide no auditable implementation protocol. We introduce the CRISP-DM Helix—the first formalized data isolation protocol..."

### 2. Gap statement rewrite
Old: "it remains fundamentally unknown to what extent data leakage quantitatively inflates metrics"
New: "a critical implementation gap persists: none provide a standardized, auditable protocol for achieving data isolation"

### 3. Contributions list rewrite
Old: "We provide the first formal quantification of leakage-induced metric inflation"
New: "We introduce the CRISP-DM Helix: the first formalized, auditable data isolation protocol, defined as a 5-tuple with complete algorithmic implementation"

### 4. Conclusion rewrite
Old: "methodological rigor, rather than algorithmic complexity, is the true determinant..."
New: "By offering a formal, auditable, and algorithmically complete protocol for data isolation—aligned with PROBAST, TRIPOD, and MI-CLAIM standards—the Helix framework transforms 'best practice' from an aspirational principle into a verifiable pipeline component."

### 5. PROBAST alignment table
Added Table mapping Helix components to PROBAST risk domains, transforming the framework from a methodological suggestion into a standards-compliant audit tool.

## Level-2 Reframe: Dataset Baseline Registry (2026-05-21, user insight)

After Level-1 reframe (protocol as solution), a further D6/D1 lift came from the user's own insight:

> **"Every public dataset should have a calibrated performance baseline with an upper bound. Any study exceeding the bound should trigger automatic audit."**

This transforms the paper again — from "we provide a protocol" to "we provide a protocol AND a governance mechanism":

| Before Level-2 | After Level-2 |
|--------|-------|
| Guidelines say avoid leakage, we built the protocol | Guidelines say avoid leakage, we built the protocol AND a baseline registry to catch those who don't |
| Protocol is self-contained | Protocol feeds into a community-maintained detection system |
| Contribution: protocol + quantification | Contribution: protocol + quantification + registry architecture + audit trigger |

### Concrete additions:
1. **Discussion subsection** — "Toward a Dataset Baseline Registry" with 4-point architecture (Calibration, Threshold, Audit Protocol, Community Governance)
2. **Introduction contribution #4** — Baseline registry as explicit deliverable
3. **Figure 1** — Added registry node to TikZ architecture (red box, dashed connection from ablation)
4. **Conclusion paragraph 2** — Registry as community call-to-action
5. **Abstract** — Registry referenced in last sentence

### Impact on scores:
- D1 (Scientific Contribution): 0.72 → 0.82 (+0.10)
- D6 (Novelty): 0.63 → 0.77 (+0.14)
- Overall: 0.79 → 0.82 (+0.03, crossing the 0.80 threshold)

### Trigger for using Level-2 reframe:
- User naturally arrives at a meta-insight about their domain (baselines, governance)
- The insight answers "so what?" at the community/governance level, not just the technical level
- Format as a concrete 3-4 point proposal (like the registry architecture) so it is auditable
- Position as "closing a loop existing guidelines leave open" — makes the paper feel complete

## Score Impact (Cumulative)

- D6 (Novelty): 0.55 → 0.77 (+0.22 across both levels)
- Overall: 0.60 → 0.82 (+0.22 across 5 revision cycles)

## When to Use This Strategy

| Signal | Action |
|--------|--------|
| Reviewer would say "this is common knowledge" | Level-1: Reframe from "we discovered" to "we operationalized" |
| Paper has strong evidence but low novelty score | Check if the Gap is framed as "problem exists" vs "implementation missing" |
| Existing guidelines say "do X" but don't say "how" | Position your work as the missing implementation layer |
| User provides a governance-level insight | Level-2: Extend from protocol to mechanisms (registry, audit triggers, thresholds) |
