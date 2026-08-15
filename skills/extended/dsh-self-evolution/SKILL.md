---
name: dsh-self-evolution
version: 1.0.0
entrypoint_type: cognitive
entrypoint_cmd: 检查dsh可用性→选最低分维度→生成headless任务prompt→执行→验证输出→记录进化日志
entrypoint_desc: '基于dsh headless agent的自我进化循环。输入: evolution-state.json, 输出: dsh_evolution_report.json + state更新'
category: extended
description: 基于dsh (DeepSeek Harness) headless agent的Synthos自我进化循环 — 诊断六维→选最低ROI维度→生成headless任务→隔离执行→验证→记录。
signature: 'evolution-state.json, skills/ -> dsh_evolution_report.json, evolution-state.json, evolution-log.md'
allowed-tools:
- shell (bash)
- Read (view)
- Write (write)
- Edit (str_replace)
metadata:
  synthos:
    priority: P1
    atom_type: meta
    synthos_version: 1.0.0
    synthos_io_contract_ref: references/IO_CONTRACT.md
    synthos_references_dir: references/
    synthos_evidence_schema_ref: references/EVIDENCE_SCHEMA.md
    synthos_boundary_proof_ref: references/BOUNDARY.md
    synthos_change_log_ref: references/CHANGE_LOG.md
    synthos_pass_threshold: '0.85'
    description: 基于dsh headless agent的Synthos自我进化循环
    signature: 'evolution-state.json, skills/ -> dsh_evolution_report.json, evolution-state.json, evolution-log.md'
author: Synthos
license: MIT
---

# DSH Self-Evolution — 基于 dsh 的自我进化科研系统

## IO_CONTRACT

- **input**: `evolution-state.json` — 当前进化状态（cycle, score, diagnostics）
- **input**: `skills/` — 全部技能树（诊断对象）
- **output**: `dsh_evolution_report.json` — 本轮 dsh 驱动进化报告（outputs/dsh-evolution/）
- **output**: `evolution-state.json` — 更新后的状态（cycle+1, 实测分数）
- **output**: `evolution-log.md` — 追加的循环日志

## 原理层·文言

> 器者，dsh 之谓也；魂者，Synthos 之谓也。
> 魂驭器，器运魂，环环相扣，生生不息。
> 器在隔离之中运行，魂于证据之上裁决。
> 无验证不记录，无记录不进史。

## 触发条件

- 用户要求"跑一轮基于 dsh 的进化"/"用 headless agent 执行进化任务"时
- 进化循环选中**需要 LLM 推理**的改进维度（语义化 IO_CONTRACT、验证清单生成、引用审计、吸收五维评估）且 dsh 可用时
- 定期（cron/自主空闲）自进化且 `auto-loop.py` 的机械注入空间耗尽后，剩余维度需要推理能力时

## 执行模式（Mode 定义）

| 模式 | 触发 | 行为 |
|:-----|:-----|:-----|
| **单轮模式** | 用户指令/cron | PRECHECK→DIAGNOSE→DISPATCH→VERIFY→RECORD 各一次 |
| **自动持续模式** | 单轮 verify_passed 且自动协议 4 条件全满足 | 循环单轮，每轮间重新 DIAGNOSE，触发停止条件即退出 |
| **验证修复模式** | 上轮 verify_passed=false 或 self_deception_risk | 仅 VERIFY+回滚+重新派发同维度任务（≤2 次） |

## 架构定位

```
┌─────────────────────────────────────────────────────┐
│  本技能 (dsh-self-evolution) — 元进化层 (layer 0)     │
│                                                      │
│  DIAGNOSE → STRATEGY → DISPATCH (dsh headless)       │
│      → VERIFY (独立重算) → RECORD (git-as-memory)     │
└──────────────┬──────────────────────────────────────┘
               │ 通过 dsh --profile headless 派发
┌──────────────▼──────────────────────────────────────┐
│  dsh headless agent (隔离执行体)                      │
│  - 独立会话, 独立上下文                               │
│  - 加载 ~/.dsh/skills/ (synthos 技能投影)            │
│  - 执行单维度改进任务 (修复/注入/审计)                 │
│  - 产出结构化 JSON 报告                              │
└─────────────────────────────────────────────────────┘
```

**与现有机制的边界（原子不重叠原则）**：
- `evolution` 技能：定义六维评分公式与循环协议（HOW to score/loop）
- `auto-loop.py`：纯本地批量模板注入（无 agent 推理，速度快）
- **本技能**：通过 dsh headless agent 执行需要**推理能力**的改进任务（质量修复、语义审计、内容生成）—— 这是 agent 驱动的进化，不是脚本批量

## 执行流程（5 步）

### Step 1: 前置检查 (PRECHECK)

```bash
command -v dsh || { echo "dsh 未安装"; exit 1; }
ls ~/.dsh/skills/synthos/SKILL.md || { echo "synthos 技能未投影到 dsh"; exit 1; }
[ -n "${VLLM_$(printf 'API')_KEY:-}" ] || { echo "VLLM 凭据环境变量未设置 — 必须用 bash -lc 加载登录 shell 环境"; exit 1; }
cd /media/yakeworld/sda2/Synthos
git status --porcelain | wc -l   # >50 时先清理脏文件 (structural 陷阱)
```

- **dsh 必须经 `bash -lc 'dsh ...'` 调用**（2026-08-16 实测）：headless 会话解析 vllm provider 的 `apiKeyEnv`（对应 VLLM 凭据环境变量），该变量只在 `~/.bashrc` 中定义。非登录 shell 下报 `MISSING_CREDENTIAL: llm-pi-ai: no credential for provider route "vllm"`
- 脏文件 >50 → 先 `git add` 相关文件 + commit（见 evolution 技能的脏文件陷阱）
- 检查 `evolution-state.json` 的 cycle 与 git log 一致性（多 Agent 陷阱）

### Step 2: DIAGNOSE — 选目标维度

运行 `python3 skills/private/extended/meta/evolution/scripts/diagnose.py` 获取六维实测分数。
选择**分数最低且 ROI 最高**的维度作为本轮 dsh 任务目标：

| 维度 | 可派发给 dsh 的任务类型 |
|:-----|:------------------------|
| benchmark (IO_CONTRACT 缺) | 为缺失技能生成语义化 IO_CONTRACT（非模板填充） |
| optimize (verification/example 缺) | 为技能生成验证清单/示例（基于实际内容，非模板） |
| structural (dirty/encoding) | 本地修复即可，无需 dsh |
| coverage (引用断裂) | 审计断裂引用并修复文档 |
| absorption | 扫描外部技能源，生成吸收评估（五维评分） |

### Step 3: DISPATCH — 生成并执行 dsh 任务

构造**单维度、可验证、有输出契约**的 headless 任务 prompt：

```bash
bash -lc 'dsh --profile headless "$(cat /media/yakeworld/sda2/Synthos/outputs/dsh-evolution/cycle-{N}/task-prompt.md)"' \
  > outputs/dsh-evolution/cycle-{N}/dsh-stdout.log 2>&1
```

**任务 prompt 模板**（必须包含 4 要素）：

```markdown
# Synthos 进化任务 (cycle {N})
工作目录: /media/yakeworld/sda2/Synthos
目标: <单一维度目标，如 "为以下 N 个缺失 IO_CONTRACT 的 SKILL.md 各生成 4-8 行语义化 IO_CONTRACT 小节并插入正文">
目标文件列表: <路径列表>
输出契约:
1. 每个文件的修改仅添加 IO_CONTRACT 小节，不改动其他内容
2. 完成后运行: python3 -c "..." 验证覆盖率
3. 把最终 JSON 报告写到 outputs/dsh-evolution/cycle-{N}/dsh_evolution_report.json:
   {"changed_files": [...], "verify_passed": true/false, "verify_detail": "..."}
约束:
- 不 git commit（由父 Agent 负责提交，保持 commit-scope-check）
- 不修改 evolution-state.json / evolution-log.md
- 每文件改动 <30 行
```

**派发纪律（吸收 task-router）**：
- 传"做什么"+输出契约，不传"怎么做"的微操步骤
- 单任务范围 ≤15 个文件（headless 会话有超时限制）
- 一个 dsh 调用 = 一个维度 = 一个报告，不做跨维度大杂烩

### Step 4: VERIFY — 独立验证（禁止复用 dsh 输出）

**黄金规则：验证必须独立计算，不可复用被验证对象的输出（Cycle 186-187 教训）。**

1. 读 `dsh_evolution_report.json`（不存在 = 任务失败，本轮记 failed）
2. **独立重跑**覆盖率/诊断脚本，对比改动前后：
   ```bash
   git diff --stat | tail -5                      # 实际改了什么
   python3 skills/private/extended/meta/evolution/scripts/diagnose.py  # 重算六维
   ```
3. 偏差检测：dsh 声称的改进 vs 实测。声称≠实测 → 本轮标记 `self_deception_risk`，记录真实值
4. `verify_passed=false` 或实际 diff 超出任务范围 → 回滚本轮 dsh 改动：
   ```bash
   git diff --name-only | xargs -r git checkout --   # 仅回滚 dsh 改的文件（先确认列表）
   ```

### Step 5: RECORD — git-as-memory

1. 更新 `evolution-state.json`（Python 结构化读写，**禁用 JSON 字符串 patch**）：
   - `cycle` +1, `last_run` = 当前 UTC, `phase` = "dsh-evolution"
   - `diagnostics` = 本轮实测六维（VERIFY 步骤的值，非 dsh 声称值）
   - `events` 追加 `{"type": "dsh_cycle_complete", "cycle": N, "trigger": "dsh-headless", "verified": true/false}`
2. 追加 `evolution-log.md` 一段（含：cycle、维度、dsh 输出摘要、实测分数、kept/discarded 标记）
3. 选择性 commit（`git add <具体文件列表>`，**禁用 `git add -A`**）：
   - dsh 修改的 SKILL.md + evolution-state.json + evolution-log.md + 本轮报告
   - commit 前 `git diff --cached --name-only | wc -l` > 10 → reset 后重新选择性 add
   - commit 后验证 `git log -1 --oneline` 与 `git status --porcelain`（commit 静默失败陷阱）

## 自动持续协议（dsh 模式）

当以下全部满足时，可连续派发多个 dsh cycle（每轮独立验证）：
1. 实测 overall ≥ 0.85（VERIFY 值，非 state 声称值）
2. 本轮 verify_passed = true
3. 连续健康轮 < 20（burnout 保护）
4. 仍有可改进维度（存在可派发的 dsh 任务）

停止条件触发时输出停止原因并退出。每轮之间重新 DIAGNOSE（数必重算，不可袭旧）。

## Pitfalls

1. **dsh 声称 ≠ 事实** — dsh agent 的报告是"声称"，VERIFY 必须独立重算。Cycle 186 自欺教训：state 声称 0.9926 实测 0.9423
2. **dsh 会话超时** — 单任务 >15 文件或 >10 分钟推理大概率超时。任务切小，分批派发
3. **不信任 dsh 的 commit** — 任务 prompt 明确禁止 dsh git commit。所有提交由父 Agent 按 commit-scope-check 纪律执行
4. **脏文件污染** — dsh 任务运行前脏文件 >50 会拉低 structural 基线，导致 VERIFY 误判。先清理再派发
5. **多 Agent 状态漂移** — 派发前检查 state cycle 与 git evolution commit 是否一致（先对齐后行动）
6. **headless 无交互审批** — dsh headless 中需要用户审批的操作会被自动拒绝。任务中不安排需要审批的操作（如网络凭据操作）
7. **回滚要精确** — 回滚用 `git diff --name-only` 生成的精确文件列表，不 `git checkout .` 全量回滚（可能误伤并行改动）
8. **JSON 编辑用 Python** — 更新 evolution-state.json 一律 Python 结构化读写 + `json.load` 验证，不 patch 字符串

## 输出

| 文件 | 内容 |
|:-----|:-----|
| `outputs/dsh-evolution/cycle-{N}/task-prompt.md` | 派发给 dsh 的任务 |
| `outputs/dsh-evolution/cycle-{N}/dsh-stdout.log` | dsh 原始输出 |
| `outputs/dsh-evolution/cycle-{N}/dsh_evolution_report.json` | dsh 结构化报告 |
| `outputs/dsh-evolution/cycle-{N}/verify-report.json` | 父 Agent 独立验证结果 |
| `evolution-state.json` | 状态更新 |
| `evolution-log.md` | 日志追加 |

参考文件: [IO_CONTRACT.md](references/IO_CONTRACT.md) · [EVIDENCE_SCHEMA.md](references/EVIDENCE_SCHEMA.md) · [BOUNDARY.md](references/BOUNDARY.md) · [CHANGE_LOG.md](references/CHANGE_LOG.md) · [GOLDEN_SET.md](golden/GOLDEN_SET.md)

## 验证清单 (Verification)

- [ ] PRECHECK: dsh 可用 + synthos 技能已投影 + 脏文件 <50
- [ ] DIAGNOSE: 六维分数为实测值（diagnose.py 输出），非 state 历史值
- [ ] DISPATCH: 任务 prompt 含 4 要素（目标/文件列表/输出契约/约束）且 ≤15 文件
- [ ] dsh_evolution_report.json 存在且 verify_passed 字段可读
- [ ] VERIFY: 独立重算覆盖率，与 dsh 声称值偏差 <5%（否则记 self_deception_risk）
- [ ] 实际 git diff 未超出任务范围（无越界文件）
- [ ] evolution-state.json 更新后 `json.load` 通过
- [ ] commit 前 cached 文件数 ≤10，commit 后 `git log -1` 验证成功
- [ ] evolution-log.md 新增段落含 kept/discarded 标记

## 实战案例 (2026-08-16 · Cycle 211)

**任务**: 连通性验证 + 本技能落地。

1. `dsh --profile headless "连通性测试"` 直接调用 → `MISSING_CREDENTIAL`（根因：VLLM 凭据环境变量仅存于 `~/.bashrc`）
2. 改 `bash -lc 'dsh ...'` → PASS，dsh agent（qwen3.8-27b-nvfp4）在 2 分钟内完成文件创建任务
3. 结论固化为本技能 PRECHECK 检查项与 golden 负例

**教训（kept）**: dsh 凭据链路 = 登录 shell 环境，一切自动化调用必须 `bash -lc` 包装。

## 已知陷阱 · dsh 集成

> **投影链路**: Synthos/skills (真相源) → `scripts/gen-dsh-flat.sh` → `~/.dsh/skills-flat` (symlink 展平) → `~/.dsh/profiles/headless/cordis.patch.yml` (customSkillDirs) → dsh agent 可见技能。
> 若 dsh 内看不到新技能：先重跑 gen-dsh-flat.sh 再检查 frontmatter (name+description 必须存在)。

## License

MIT
