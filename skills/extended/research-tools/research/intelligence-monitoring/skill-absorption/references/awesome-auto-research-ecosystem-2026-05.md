# Awesome Auto Research Ecosystem Snapshot (2026-05-15)

> Source: [Awesome-Auto-Research-Tools](https://github.com/handsome-rich/Awesome-Auto-Research-Tools) ⭐427
> Last verified: 2026-04-22 by list author; re-verified 2026-05-15 via gh CLI
> Purpose: Quick-reference map of the automated research ecosystem for absorption gap analysis

---

## 🧪 端到端自主研究系统 (End-to-End Systems)

| Project | ⭐ | Framework | Philosophy | Notes |
|---------|---|-----------|------------|-------|
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | ~18k | Custom (PyTorch, nanochat) | Minimalist 630-line agent, hypothesis→code→experiment loop | Origin of the "auto research" concept |
| [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist) | ~13.5k | Custom templates + LaTeX | First comprehensive automated discovery system | Fully autonomous idea→paper |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | ~13k | LiteLLM + Docker + Qlib | R&D automation (quant, Kaggle) | Top MLE-bench agent |
| [aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) | ~12k | OpenClaw + Docker + LaTeX | Open-source research agent with sandbox | Strong multi-agent peer review |
| [wanshuiyin/ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | ~9.3k | Claude Code + MCP | Lightweight Markdown-only skills | Directly comparable to Synthos paradigm |
| [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) | ~8k | BFTS agentic tree search | Upgraded with tree search for experiments | First AI-written accepted workshop paper |
| [HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) | ~4.5k | LiteLLM + Docker + Gradio | NeurIPS'25 Spotlight | Covers full pipeline |
| [SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | ~4k | Custom multi-agent | End-to-end with specialized agents | Literature→experiment→report |
| [Galaxy-Dawn/claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) | ~2.5k | Claude Code + Zotero MCP | Semi-automated academic research | Zotero + Obsidian integration |
| [snap-stanford/Biomni](https://github.com/snap-stanford/Biomni) | ~1k | Custom biomedical agent | Stanford biomedical AI agent | Domain-specific (bio/med) |
| [ResearAI/DeepScientist](https://github.com/ResearAI/DeepScientist) | ~800 | Bayesian opt + Findings Memory | Local-first autonomous research studio | Unique Findings Memory for experiment tracking |
| [starpig1129/DATAGEN](https://github.com/starpig1129/DATAGEN) | ~600 | LangChain + LangGraph | Multi-agent research assistant | Hypothesis→data→report |
| [InternScience/InternAgent](https://github.com/InternScience/InternAgent) | ~400 | Custom + Aider | Unified agentic framework (physics, bio) | Shanghai AI Lab |

## 📚 深度调研与文献综合 (Deep Research & Literature)

| Project | ⭐ | Framework | Distinction | Notes |
|---------|---|-----------|-------------|-------|
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | ~5k | LangChain + LangGraph | ByteDance SuperAgent | InfoQuest integration |
| [stanford-oval/STORM](https://github.com/stanford-oval/STORM) | ~16k | DSPy + LiteLLM | Wikipedia-style article generation | Co-STORM human-in-loop |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | ~27k | LangGraph + MCP | Deep research + web | Most starred research agent |
| [kaixindelele/ChatPaper](https://github.com/kaixindelele/ChatPaper) | ~13k | PyMuPDF + Flask | arXiv paper summarization | Established pioneer |
| [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | ~2k | Custom ReAct + GRPO RL | 30B-A3B model | SOTA on multiple benchmarks |
| [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) | ~5k | LangChain + LangGraph | MCP-configurable deep research | LangChain official |
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) (PaperQA2) | ~10k | LiteLLM + tantivy | High-accuracy scientific RAG | Published at ICLR |
| [SkyworkAI/DeepResearchAgent](https://github.com/SkyworkAI/DeepResearchAgent) | ~500 | Autogenesis self-evolution | Hierarchical multi-agent with self-evolution | **Self-evolution similar to Synthos** |
| [HKUDS/Auto-Deep-Research](https://github.com/HKUDS/Auto-Deep-Research) | ~1.5k | AutoAgent + LiteLLM | OpenAI Deep Research open alternative | Strong GAIA results |
| [AkariAsai/OpenScholar](https://github.com/AkariAsai/OpenScholar) | ~3k | Custom RAG (45M papers) | Published in Nature | Outperforms PaperQA2 |
| [TIGER-AI-Lab/OpenResearcher](https://github.com/TIGER-AI-Lab/OpenResearcher) | ~800 | Megatron-LM + vLLM | Fully open training + inference | **Open-weight 30B model beats GPT-4.1** |

## ⚙️ 自动化实验与代码智能体 (Experiment & Code Agents)

| Project | ⭐ | Framework | Distinction | Notes |
|---------|---|-----------|-------------|-------|
| [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | ~170k | Custom Agent Builder | Pioneer autonomous agent | Historical significance |
| [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | ~50k | Custom agentic framework | 72% on SWE-Bench | Active development |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | ~35k | Custom CLI + Git | AI pair programming | De facto coding backbone for research |
| [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | ~14k | YAML-config | Princeton, SWE-Bench originator | Research-oriented |
| [dwzhu-pku/PaperBanana](https://github.com/dwzhu-pku/PaperBanana) | ~200 | Streamlit + OpenRouter | Multi-agent academic illustration | **Unique niche: figure generation** |
| [MLSysOps/MLE-agent](https://github.com/MLSysOps/MLE-agent) | ~1k | Python + Kaggle | ML engineering companion | arXiv + Papers with Code |
| [WecoAI/aideml](https://github.com/WecoAI/aideml) (AIDE) | ~3k | Agentic tree search | Kaggle: 4× medals over linear agents | Published paper |

## 🔧 研究 Skills 与插件合集 (Skill Collections)

| Project | ⭐ | Size | Platform | Notes |
|---------|---|------|----------|-------|
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | ~800 | 133 skills | Claude Code, Cursor, Codex | Bio/med/imaging focus |
| [Orchestra-Research/AI-research-SKILLs](https://github.com/Orchestra-Research/AI-research-SKILLs) | ~1.2k | 86 skills (22 categories) | Claude Code, Codex, Gemini CLI | Full AI research lifecycle |

---

## Already Tracked (cross-reference with absorption-ledger.json at /media/yakeworld/sda2/Synthos/absorption-ledger.json)

Known from prior scanning:
- karpathy/autoresearch — already in tracking (absorbed into research-ideation)
- SakanaAI/AI-Scientist — already evaluated (gap-fit: weak)
- microsoft/RD-Agent — already in tracking
- aiming-lab/AutoResearchClaw — Phase 0 completed (2026-05-10)
- wanshuiyin/ARIS — already evaluated (gap-fit: partially absorbed via evolution)
- stanford-oval/STORM — already tracked
- Future-House/paper-qa (PaperQA2) — already tracked
- assafelovic/gpt-researcher — already tracked
- kaixindelele/ChatPaper — already tracked

## New Candidates for Absorption Evaluation

| Project | Category | Score | Priority | Why |
|---------|----------|:-----:|:--------:|:----|
| ResearAI/DeepScientist | End-to-end | TBD | 🔥 High | Findings Memory + Bayesian opt unique — Synthos has no experiment tracking |
| SakanaAI/AI-Scientist-v2 | End-to-end | TBD | 🔥 High | BFTS tree search — could enhance evolution engine |
| TIGER-AI-Lab/OpenResearcher | Literature | TBD | ⭐ Medium | Open-weight model for deep research |
| SkyworkAI/DeepResearchAgent | Literature | TBD | ⭐ Medium | Self-evolution protocol (Autogenesis) — parallel to Synthos |
| dwzhu-pku/PaperBanana | Experiment | TBD | ⭐ Medium | Multi-agent figure generation — could enhance figure-generation skill |
| K-Dense-AI/scientific-agent-skills | Skills | TBD | 📋 Track | 133 scientific skills — large surface area to scan |
| Orchestra-Research/AI-research-SKILLs | Skills | TBD | 📋 Track | 86 SKILL.md skills — directly comparable format |
