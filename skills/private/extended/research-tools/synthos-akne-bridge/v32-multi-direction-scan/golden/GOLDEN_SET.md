# Golden 集合 · v32-multi-direction-scan

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 对应 SKILL.md「Golden 集合 · GOLDEN SET」小节（SK-007/008）。

## 语义

本技能对 v32 轮换方向（5 个 rotation + 5 个 new exploration）执行多方向文献扫描
（PubMed 定向 + OpenAlex broad/cited），前置 Step 0 模式决策以对齐
paper-pipeline 9 核心约束。Golden 集合覆盖：

- **正常路径**：Step 0 通过 → 各方向扫描 → 结果表（无 Cycle 245 vhit 漂移）。
- **错误路径**：请求描述/上下文缺失或无效 → 输入验证阻断 + 含上下文与恢复指引的错误信息。

## 测试用例表

| Case | 类型 | 输入要点 | 期望要点 | 验证基因 |
|------|------|----------|----------|----------|
| `case_001_normal` | 正常 | 5 个轮换方向 + Step 0 已对齐 9 约束 | `success`；5 行结果表（PubMed + OpenAlex 均执行、status ∈ {ABSOLUTE_WHITE, has_competition, in_progress}、score∈[0,1]）；过程验证确认无 vhit 漂移 | SK-001/004/005 |
| `case_002_error` | 错误 | directions 为空 + Step 0 未完成 | `error`；`scan_executed=false`（流程被阻断）；错误信息含上下文与恢复指引 | SK-002/006 |

## 通过标准

1. 每个 case 的 `expected_status` 与实际执行状态一致（success/error）。
2. 正常 case：`scan_results` 覆盖输入 directions 的全部方向，每行含
   `pubmed_targeted_query=executed` 且 `openalex_broad_cited=executed`；
   `process_verification.no_cycle245_vhit_drift=true`；输出格式符合 IO_CONTRACT（SK-005）。
3. 错误 case：`blocked=true` 且 `scan_executed=false`（SK-002 阻断生效）；
   `error.message_must_include` 中两条（上下文、恢复指引）均出现在实际错误信息中（SK-006）。
4. 每个 case 可独立复现：同输入二次执行结果一致（P1 原子可复现性）。
5. 验证失败时必须记录原因与修复措施（SK-008）。

## 文件布局

```
golden/
├── GOLDEN_SET.md          # 本文件（语义 + 用例表 + 通过标准）
├── cases/
│   ├── case_001_normal.json
│   └── case_002_error.json
└── expected/
    ├── case_001_normal.json
    └── case_002_error.json
```
