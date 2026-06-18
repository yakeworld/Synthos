# CHANGE_LOG.md — argument-expression

> 对应原则：P3（受控变更留痕）
> 文件 hash 清单（SHA-256）：

| 文件 | hash |
|------|------|
| SKILL.md | `<PENDING>` |
| references/IO_CONTRACT.md | — |
| references/EVIDENCE_SCHEMA.md | — |
| references/BOUNDARY.md | — |
| golden/GOLDEN_SET.md | — |

---

## v0.1.0 — 2026-05-10

**变更类型**: 初始版本
**描述**: 创建 argument-expression 认知原子。定义 SKILL.md、IO_CONTRACT、EVIDENCE_SCHEMA、BOUNDARY、GOLDEN_SET。金标准为 self_defined，5 个测试用例覆盖不同 IMRaD 结构（introduction、methods、discussion、full_paper）和边缘案例（无 raw_papers、空假设列表）。
**影响的组件**: argument-expression（全部）
**审批人**: Synthos Agent
**审批时间**: 2026-05-10
**金标准通过率**: 待首次测试

---

## v0.2.0 — 2026-05-14

**变更类型**: [PW-Bench吸收] 质量门控增强
**描述**: 
- 从 PaperOrchestra/PaperWritingBench (arXiv:2604.05018, App. F.3) 吸收文献综述六轴质量评分体系
- 在 §7 质量要求中新增 6 轴评分门控（Coverage/Relevance/Critical Analysis/Positioning/Organization/Citation Rigor）
- 门控阈值：≥55 直接输出，40-54 标注改进点，<40 标记重写
- 新增 reference 文件: references/litreview-quality-gate.md
- 反膨胀规则：默认期望 45-70，>85 需六轴全强证据
**影响的组件**: SKILL.md (§7 + references索引), CHANGE_LOG.md
**审批人**: Synthos Agent
**审批时间**: 2026-05-14
