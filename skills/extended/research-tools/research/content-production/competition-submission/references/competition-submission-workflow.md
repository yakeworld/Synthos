# Competition Submission Workflow — End-to-End

This reference documents the complete workflow for preparing and submitting competition materials, extracted from real sessions (e.g., 全球数智教育创新大赛 AI for Medicine 赛道).

## Full Workflow

```
PDF/URL → Extract Requirements → Analyze Project → Map to Scoring → Generate Materials → Review → Submit
```

### Step 1: Extract Requirements (PDF/URL)

```bash
# For PDF:
pdftotext "/path/to/competition.pdf" - > /tmp/competition.txt

# For website (avoid browser_navigate — timeouts):
curl -sL --max-time 60 -H "User-Agent: Mozilla/5.0 ..." "https://..." | grep -oP '...' 

# Key fields to find:
# - 报名截止时间 (deadline)
# - 材料要求 (required materials)
# - 评分标准 (scoring criteria)
# - 参赛对象 (eligibility)
# - 赛组设置 (categories/tracks)
```

### Step 2: Analyze Project

1. Read all project documentation (SKILL.md, README.md, architecture docs)
2. For NotebookLM-based projects: `notebooklm source list` → `notebooklm summary`
3. Identify: core features, innovations, validation data, user base, scalability
4. Map each feature to scoring criteria

### Step 3: Generate Materials (ALL in parallel)

| Material | Word Limit | Key Content |
|----------|-----------|-------------|
| 建设说明书 | ≤3000字 | 概述2000字 + 应用成效1000字 |
| 技术路线图 | 无限制 | 架构图 + 数据流 + 进化流程 + 技术栈 |
| 演示视频脚本 | 6-10分钟 | 旁白+画面+时间戳 |
| 申报书模板 | 按官网格式 | 所有字段预填好 |
| 承诺书 | 按大赛要求 | 逐条映射项目实际 |
| 配套材料清单 | 无限制 | 状态追踪 (✅/⏳) |
| 总索引 | 无限制 | 所有材料索引 + 评分匹配 + 行动清单 |

### Step 4: Review & Cross-Check

- [ ] Word counts within limits
- [ ] Identity anonymization (no names, no school names in videos/materials)
- [ ] File naming conventions correct
- [ ] All mandatory materials included
- [ ] Video format: MP4, 720p+, 6-10 min
- [ ] Professional category correct (临床医学类 for medical AI)
- [ ] Commitment letter clauses mapped to project context
- [ ]申报书 PDF: user fills on website, exports, gets stamped

### Step 5: Deliver & Track

Generate `SUBMISSION_PLAN.md` with:
- All materials status
- Action items for the user
- Deadline countdown
- Contact info for the competition

## Post-Refactoring Material Alignment Audit

After a project undergoes major restructuring (file deletion, version upgrade, architecture change), ALL competition materials that reference system internals must be audited.

### Typical Discrepancies Found in a Real Audit (Synthos v3→v4.2)

| File | Issue | Fix |
|------|-------|-----|
| `synthos-audit-report.md` | Version 3.0.0 → 4.2.0; scores stale (68%→85%); refs scripts/ | Update version, rescore, replace script refs with skill-driven description |
| `falsification-summary.md` | Refs core/atom0_*.py (deleted); old file tree | Replace with skills/*/SKILL.md tree; update scores |
| `skill-tree-exploration.md` | Describes 14 Python scripts + integration plan (no longer exists) | Archive with header: "v3.1 — superseded by v4.2" |
| `技术路线图.md` | Tech stack table lists skill_network.py, evolution_scheduler.py | Replace with 任务路由器 SKILL.md, 进化引擎 SKILL.md |
| `智能体建设说明书.md` | Data layer refs skill_registry.json, skill_network.json | Replace with evolution-state.json + trust_db.json |

### Audit Checklist

1. **版本号** — grep for "3.0.0", "v3", "version: 3" across all docs
2. **已删除文件** — grep for any filename that was in core/ or scripts/
3. **指标** — compare reported scores/metrics vs current evolution-state.json
4. **文件结构** — if the doc shows a tree diagram, verify it matches actual `tree` output
5. **技术组件** — check tech stack tables for scripts that no longer exist
6. **视频** — check if the video shows the old UI/code structure (re-render decision)

## Real Session Example: 全球数智教育创新大赛

**Competition**: 全球数智教育创新大赛 AI for Medicine 赛道
**Deadline**: 2026-05-15 15:00
**Project**: Synthos — 自主进化学术科研平台
**Materials Prepared**: 10 core files in 1 session
**Key Enhancement**: Integrated 73 teaching sources from NotebookLM as core application case
**Score Impact**: +5-8 points from teaching project integration
**Professional Category**: 临床医学类 / 临床医学（AI辅助临床科研与教学）

## Common Competition Types

| Type | Key Requirements | Typical Deadline |
|------|-----------------|------------------|
| Medical AI education | 建设说明书 + 视频 + 申报书 + 承诺书 | 2-4 weeks |
| General tech innovation | 项目计划书 + demo视频 + PPT + 商业分析 | 4-8 weeks |
| Academic conference | Abstract + full paper + author info | 8-16 weeks |
| Government grant | 申请书 + 预算表 + 伦理审批 + 伦理批件 | 2-6 months |
