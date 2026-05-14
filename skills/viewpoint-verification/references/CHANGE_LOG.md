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

---

## v0.2.0 — 2026-05-13

**变更类型**: [ARS吸收] 能力增强
**描述**: 
- 在 SKILL.md 推理流程中新增 Step 4（反谄媚门控 — Concession Threshold Protocol）
- 用户反驳必须打分1-5才能让步（5=让步，4=让步但标注缺口，3=坚守，2=反攻，1=升级）
- 禁止连续让步（让步后下次门槛升到5/5）
- 让步率 >50% 时暂停并升级所有门槛到5/5
- 思维框锁检测（每3轮反驳后自问前提假设）
- 反模式警告：用户坚持≠证据，用户情绪不影响验证
- 新增 frontmatter: `synthos_data_access_level: "verified_only"`
**影响的组件**: SKILL.md, frontmatter
**审批人**: Synthos Agent
**审批时间**: 2026-05-13

---

## v0.3.0 — 2026-05-14

**变更类型**: [PW-Bench吸收] 证据质量增强
**描述**: 
- 从 PaperOrchestra/PaperWritingBench (arXiv:2604.05018, App. F.3) 吸收 Citation F1 引用质量评价方法论
- 在置信度计算步骤（Step 3e）之后新增 Step 3e.5：引用质量修正门控
- 引用质量得分 = (P0数 + 0.5×P1数) / (P0数 + P1数)
- 置信度修正：confidence × min(1.0, citation_quality + 0.3)
- 新增 reference 文件: references/citation-f1-methodology.md
- P0/P1 分类不参与自动裁决，仅作为弱信号
**影响的组件**: SKILL.md (Step 3e.5 + references索引), CHANGE_LOG.md
**审批人**: Synthos Agent
**审批时间**: 2026-05-14
