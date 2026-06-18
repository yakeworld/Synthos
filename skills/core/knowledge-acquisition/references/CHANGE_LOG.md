# CHANGE_LOG.md — knowledge-acquisition

## v1.6.0 — 2026-06-06

**变更类型**: 核心修复 — NCBI eFetch retmode=json 系统性破坏
**描述**: NCBI June 2026 API 变更导致 eFetch 的 retmode=json 对单 ID 请求返回原始整数（非 JSON）。所有 eFetch 调用必须使用 retmode=xml。此修复已在 `research-paper-search` skill 中记录（`references/efetch-response-quirks.md` v31）。所有 PubMed eFetch 相关代码已验证使用 retmode=xml（无中断）。
**影响的组件**: knowledge-acquisition, research-paper-search, autonomous-core-researcher（所有依赖 PubMed eFetch 的技能）

## v1.5.0 — 2026-05-18

**变更类型**: 核心规范强制 — 写作闭环审计驱动
**描述**: 新增三条铁律：(1) 严禁模拟输出——所有文献必须真实搜索/下载，不存在则如实报告0篇；(2) PDF以BibTeX key命名（Author2024.pdf）；(3) 摘要元数据以.bib格式保存到references/目录。**多关键词搜索策略**：每个主题至少用3个关键词变体（核心词→同义词→方法学→中英文→拓展词）并行搜索，limit=100。**质量门槛**：本论文自身应引用≥40篇参考文献——检索目标80-120篇候选，去重保留60+篇供引用筛选。所有API默认limit=100。
**触发原因**: 写作闭环审计发现8/8原子被模拟而非真正调用，用户明确要求强制规范。
**影响的组件**: knowledge-acquisition (SKILL.md + 输出契约)
**审批人**: Hermes Agent (autonomous — 写作闭环审计驱动)
**审批时间**: 2026-05-18

## v1.4.0 — 2026-05-18

**变更类型**: 架构增强 — API弹性层
**描述**: 新增本地缓存系统(outputs/search-cache/)、API回退链(6级优先级+离线兜底)、local_absorption_db离线数据源。任何源失败自动降级，连续2源失败启用过期缓存，连续3源失败使用吸收库兜底。
**触发原因**: 写作闭环测试发现S2 API完全不可用，ACQ无法完成搜索。
**影响的组件**: knowledge-acquisition (SKILL.md 执行流程 + 输出契约)
**审批人**: Hermes Agent (autonomous — 写作闭环测试驱动)
**审批时间**: 2026-05-18

## v1.3.0 — 2026-05-11
**变更类型**: 引用验证（CITATION_VERIFICATION.md）

## v1.2.0 — 2026-05-11
**变更类型**: 新增bioRxiv/medRxiv

## v1.1.0 — 2026-05-11
**变更类型**: 4层引用验证

## v1.0.0 — 2026-05-10
**变更类型**: 初始版本 (Python→Agent-native)
