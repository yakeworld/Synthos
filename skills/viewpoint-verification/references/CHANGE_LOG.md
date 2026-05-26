# CHANGE_LOG.md — viewpoint-verification

> 对应原则：P3（受控变更留痕）
> 文件 hash 清单（SHA-256）：

| 文件 | hash |
|------|------|
| SKILL.md | `9224c10a88b51c...` |
| references/IO_CONTRACT.md | — |
| references/EVIDENCE_SCHEMA.md | — |
| references/BOUNDARY.md | — |
| golden/GOLDEN_SET.md | — |

---

## v0.1.0 — 2026-05-10

**变更类型**: 初始版本
**描述**: 创建 viewpoint-verification 认知原子（原子6），遵循 knowledge-extraction 黄金模板结构。定义 SKILL.md、IO_CONTRACT、EVIDENCE_SCHEMA、BOUNDARY、GOLDEN_SET。金标准为 self_defined，4 个测试用例覆盖：明确反方观点、充分支持、证据不足、需修订等场景。

**新增文件**:
- SKILL.md — 原子定义，含 frontmatter、职责、流程、示例
- references/IO_CONTRACT.md — 输入输出 schema（Verification、CounterArgument、verdict 枚举）
- references/EVIDENCE_SCHEMA.md — 5 种证据节点类型（doi、atom_output、reasoning、falsification_test、robustness_check）
- references/BOUNDARY.md — 6 原子非重叠性证明 + 边界模糊案例裁决
- golden/GOLDEN_SET.md — 4 个自设金标准测试用例

**依赖声明**: 上游依赖 `hypothesis-generation`（原子4）和 `argument-expression`（原子5）。不向下游传递（终端原子）。

**影响的组件**: viewpoint-verification（全部）
**审批人**: Synthos Agent
**审批时间**: 2026-05-10
**金标准通过率**: 待首次测试
