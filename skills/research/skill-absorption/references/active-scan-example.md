# Active Scan Worked Example (2026-05-11)

## Context

First run of the Active Absorption Engine v3.0 on Synthos v4.2.0.
10 keyword groups scanned in parallel, 15 projects discovered.

## Keywords Used

| Group | Keywords | Results |
|-------|----------|---------|
| A | "autonomous research agent" OR "scientific discovery agent" | BioAgents(152⭐), Mimosa-AI(22⭐), redigg, ADM-3 |
| B | "cognitive architecture" OR "agent skill framework" | KILO-KIT(24⭐) — Cognitive Flow + skill-md |
| C | "paper generation" OR "academic writing agent" OR "latex agent" | PaperForge(554⭐), SCI-Writting-Agenet(1⭐) |
| D | "knowledge graph research" OR "literature mining" | Multiple small projects |
| E | "hypothesis generation" OR "scientific claim verification" | Sakana AI-Scientist(13.5k⭐) |

## Top Discoveries

| Project | Stars | Score | Gap Filled | Decision |
|---------|-------|-------|------------|----------|
| Sakana AI-Scientist | 13.5k | 5.0 | End-to-end paper generation pipeline | evaluating |
| KILO-KIT | 24 | 5.0 | Cognitive Flow + skill-md + subagent | evaluating |
| ResearcherSkill | 218 | 5.0 | skill.md-driven experiment automation | evaluating |
| paper-qa | 8.5k | 3.9 | RAG + citation generation | evaluating |
| PaperForge | 554 | 4.0 | Paper generation pipeline | tracking |
| Mimosa-AI | 22 | 4.0 | Self-evolving workflow + MCP | tracking |

## Self-Discovered Keywords (63 new)

cognitive-flow-architecture, skill-md, subagent-system, cbu, pce,
template-based-generation, automated-review, multi-agent-science,
self-evolving-workflow, mcp-tool-discovery, agent-orchestration,
paper-generation, end-to-end-pipeline, experiment-automation,
single-file-skill, codex-integration, cursor-integration,
journal-style-analysis, citation-formatting, multi-agent-writing,
full-automation, open-ended-discovery, template-paper,
deep-research, web-scraping, rag, scientific-qa,
multi-llm, research-automation, prompt-patterns,
human-augmentation, modular-prompts, crowdsourced-patterns,
autonomous-agents, plugin-ecosystem, long-term-memory,
tool-integration, multi-agent-conversation

## Key Lessons

1. **skill.md paradigm is a real trend** — KILO-KIT, ResearcherSkill, and Fabric all use similar single-file skill patterns. This validates Synthos's architecture choice.
2. **Small projects can be more insightful than large ones** — KILO-KIT(24⭐) has the most architecturally similar approach to Synthos.
3. **Keywords self-expand rapidly** — 10 initial keywords to 73 after one scan.
4. **Prioritize absorption candidates by architecture fit, not star count** — Sakana(13.5k⭐) is Python-heavy; KILO-KIT(24⭐) is skill-md native.
