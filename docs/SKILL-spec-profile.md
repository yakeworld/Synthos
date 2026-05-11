# SKILL-spec-profile.md

**文档类型**：Synthos SKILL 规范扩展档案（Spec Profile）
**基础规范**：[Agent Skills Specification](https://agentskills.io/specification)
**依赖宪法**：SKILL-principles.md v1.0-final
**版本**：1.0-final
**状态**：定版

---

## 0. 本文档的定位

本文档是 Synthos 与 Agent Skills 标准之间的**适配层**。它回答一个问题：**"当 Synthos 的某个原子要写 SKILL.md 时，它必须遵守什么？"**

它**不是**架构文档——不描述原子之间如何协作。
它**不是**宪法文档——不产生新的原则性约束。
它**是**一份**字段级、语法级、文件级**的精确规约，服务于 6 个认知原子 SKILL.md 的平行开发。

**继承关系**：
```
Agent Skills Spec（外部标准，不可改）
        ↓ 被扩展
SKILL-spec-profile.md（本文档 - Synthos 适配层）
        ↓ 被遵守
6 × 认知原子 SKILL.md（实例）
```

---

## 1. 基础规范声明

Synthos 所有认知原子的 SKILL.md **必须无条件符合** Agent Skills Specification 的全部硬性约束，包括：

- 目录结构：SKILL.md 位于原子目录根部
- `name` 字段：1-64 字符，小写字母数字连字符，匹配父目录名，不以连字符首尾，无连续连字符
- `description` 字段：1-1024 字符，非空
- YAML frontmatter + Markdown 正文结构
- 文件引用：相对路径，一层深度
- 正文规模：≤ 500 行、≤ 5000 tokens（推荐值，Synthos 升级为**硬约束**）

**不符合基础规范的 SKILL.md 一律拒收**，无论 Synthos 扩展字段多完善。

---

## 2. Synthos 扩展字段规约（metadata 命名空间）

### 2.1 命名规则

所有 Synthos 扩展字段**必须**位于 frontmatter 的 `metadata` 映射下，且键名**必须**以 `synthos_` 为前缀。

规范允许 metadata 存储 **string → string** 映射。复杂结构必须序列化为 JSON 字符串，或外置到文件后在此处存引用路径。

### 2.2 字段清单（v1.0）

| 字段名 | 必填 | 类型 | 说明 | 对应原则 |
|---|---|---|---|---|
| `synthos_atom_type` | 是 | 枚举字符串 | `cognitive` / `mechanical` / `router` | 架构标识 |
| `synthos_version` | 是 | 语义版本字符串 | 如 `"1.0.0"`，遵循 SemVer | P3 |
| `synthos_skill_md_hash` | 是 | SHA-256 十六进制字符串 | 自动计算，见 §3 | P1, P3 |
| `synthos_model_version_pin` | 是 | 字符串 | 最后一次通过金标准的模型，格式 `provider/model_id@version` | P1 |
| `synthos_model_tested_on` | 是 | ISO 8601 日期时间字符串 | 最后一次金标准测试通过的时间 | P1 |
| `synthos_io_contract_ref` | 是 | 相对路径字符串 | 指向 IO 契约文件 | P2 |
| `synthos_evidence_schema_ref` | 是（认知原子）| 相对路径字符串 | 指向证据链 schema 文件 | P0 |
| `synthos_golden_set_ref` | 是（认知原子）| 相对路径字符串 | 指向金标准说明文件 | P1 |
| `synthos_golden_set_origin` | 是（认知原子）| 枚举字符串 | `external` / `self_defined` / `hybrid` | P1 |
| `synthos_pass_threshold` | 是（认知原子）| 浮点数字符串 | 如 `"0.85"`，范围 [0, 1] | P1 |
| `synthos_boundary_proof_ref` | 是（认知原子）| 相对路径字符串 | 指向边界证明文件 | P2 |
| `synthos_change_log_ref` | 是 | 相对路径字符串 | 指向变更日志文件 | P3 |
| `synthos_asserted_compliance` | 是 | 逗号分隔字符串 | 如 `"P0,P1,P2"`，原子维护者签名式声明已满足的原则 | 元数据 |
| `synthos_mechanical_atoms` | 是 | 逗号分隔字符串 | 本原子允许调用的机械原子 canonical_id 白名单（**权威来源**）| P2 |
| `synthos_depends_on` | 否 | 逗号分隔字符串 | 本原子上游依赖的其他认知原子名 | 架构 |
| `synthos_author` | 否 | 字符串 | 维护者标识 | 元数据 |

### 2.3 枚举值约束

**`synthos_atom_type`** 可选值：
- `cognitive`：认知原子（6 个之一）
- `mechanical`：机械原子（工具箱成员）
- `router`：路由器（结构上特殊的认知原子）

**`synthos_golden_set_origin`** 可选值：
- `external`：金标准来自外部权威（公开数据集、标注语料等）
- `self_defined`：原子自行设计的金标准（必须在 GOLDEN_SET.md 中说明设计依据）
- `hybrid`：混合型，部分外部 + 部分自定义

**`synthos_asserted_compliance`** 取值规则：
- 对认知原子恒为 `"P0,P1,P2"`；对机械原子恒为 `"P2,P3"`。
- **必须显式写出，不允许"默认推导"**。此字段是签名式声明——原子维护者主动确认"我已满足这些原则"。
- 若事后审计发现某条原则未满足，此字段提供了可追责的声明记录（P0 自洽：元数据本身也是证据）。

### 2.4 `synthos_model_version_pin` 格式规约

语法：`provider/model_id@version`，三段均为 `[a-z0-9._-]+`。

| 段 | 含义 | 示例 |
|----|------|------|
| `provider` | 厂商标识 | `anthropic` / `deepseek` / `openai` / `local` |
| `model_id` | 厂商内部的模型名 | `claude-opus-4.7` / `deepseek-v4-pro` |
| `version` | 厂商发布的版本标识符，**优先使用厂商官方版本号**，无则退回日期 | `2026-05-10` / `2.1.0` |

示例：`deepseek/deepseek-v4-pro@2026-04-22`、`anthropic/claude-opus-4.7@2026-05-10`

`synthos_model_version_pin` 与 `synthos_model_tested_on` 配合使用：前者记录**什么模型**通过测试，后者记录**什么时候**通过。两者必须一起更新——只更新一个而不同步另一个视为 P1 违规。

### 2.5 字段规模上限

整个 `metadata` 映射序列化后不超过 **4 KB**。超过则必须外置到 references/。这防止 metadata 膨胀吞噬 SKILL.md 的有效空间。

---

## 3. `synthos_skill_md_hash` 计算规则

### 3.1 为什么需要这个字段

P1 要求可复现性，P3 要求变更留痕。skill_md_hash 是 SKILL.md 当前状态的**指纹**：
- 任何文本变化都会改变 hash
- 任何使用该原子的运行记录都会记录 hash
- 未来复现时，hash 不匹配 = 立即可见的警报

### 3.2 计算算法

```
1. 读取 SKILL.md 完整文本（UTF-8 编码）
2. 将 metadata.synthos_skill_md_hash 的值替换为固定占位符 "<PENDING>"
3. 对替换后的文本计算 SHA-256
4. 将计算结果（64 位十六进制小写）写回 metadata.synthos_skill_md_hash
```

**关键点**：计算时排除该字段自身的值，避免自引用悖论。实现时统一使用占位符 `<PENDING>` 作为计算占位。

### 3.3 何时重新计算

- SKILL.md 任何字符发生变化时
- 发布前的自动化流水线中强制校验
- references/ 下文件变化时**不**触发 skill_md_hash 更新（那些变化由各自的 ref 内容 hash 追踪）

### 3.4 references/ 完整性校验（附加约定）

每个 references/ 文件**自身**也应有独立 hash 记录。建议在 CHANGE_LOG.md 顶部维护一张文件 hash 清单，变更时更新。这是 P1 的延伸实施细节，不强制写入 metadata（避免字段爆炸）。

---

## 4. `allowed-tools` 双轨声明规则

### 4.1 两个字段的分工

| 字段 | 位置 | 语法 | 定位 |
|---|---|---|---|
| `allowed-tools` | frontmatter 顶级（Agent Skills 实验性字段）| 空格分隔 Agent Skills 官方语法 | **兼容层**：面向支持该字段的 client |
| `synthos_mechanical_atoms` | metadata 下 | 逗号分隔机械原子名（canonical_id） | **权威层**：Synthos runtime 的唯一信任源 |

### 4.2 一致性约束

`synthos_mechanical_atoms` 中的每个 canonical_id 在架构层映射表（SKILL-architecture.md）中有对应的 `agent_skills_name`，该 name **必须**出现在 `allowed-tools` 中。反之亦然。

由于 `allowed-tools` 是 Agent Skills 官方字段、语法可能演进，而 Synthos 需要稳定内部协议，**冲突时以 `synthos_mechanical_atoms` 为准**。

架构层映射表的每个机械原子条目必须包含：
```
canonical_id: file_reader          # Synthos 内部唯一标识
agent_skills_name: Read            # Agent Skills allowed-tools 语法
agent_skills_pattern: Read(*)      # 可选：带参数的完整表达
```

### 4.3 声明示例

```yaml
allowed-tools: Read FileSearch(*) WebFetch(allowlist)
metadata:
  synthos_mechanical_atoms: "file_reader,file_searcher,web_fetcher"
```

---

## 5. 金标准存放约定

### 5.1 目录选择

Synthos 在规范允许的 "Any additional files or directories" 条款下，在原子根目录设立**独立**目录：

```
atom-name/
├── SKILL.md
├── scripts/
├── references/
├── assets/
└── golden/              ← Synthos 专属
    ├── cases/           ← 测试用例
    ├── expected/        ← 期望输出
    └── GOLDEN_SET.md    ← 说明文档（metadata 引用此文件）
```

### 5.2 为什么独立目录而非 references/ 或 assets/

- **语义独立**：金标准是测试数据，不是参考文档，也不是静态资源模板
- **规模独立**：金标准可能远大于 SKILL.md 正文与 references/
- **更新独立**：金标准的版本演进与 SKILL.md 主体不同步（P1 要求金标准可独立演进）
- **权限独立**：未来可能对 golden/ 实施只读保护，防止为了通过测试而篡改金标准

### 5.3 metadata 中的引用

```yaml
metadata:
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
```

---

## 6. references/ 标准文件清单（认知原子必备）

每个认知原子**必须**在 references/ 下提供以下 5 份标准文件。metadata 的 `synthos_*_ref` 字段指向它们。

| 文件名 | 内容 | 对应原则 | 规模建议 | 生成方式 |
|---|---|---|---|---|
| `IO_CONTRACT.md` | 输入 schema、输出 schema、字段语义 | P2 | ≤ 300 行 | 可从 atom-io-schemas.md 模板化生成 |
| `EVIDENCE_SCHEMA.md` | 证据链数据结构、字段约束、示例 | P0 | ≤ 200 行 | 可从 atom-io-schemas.md 模板化生成 |
| `BOUNDARY.md` | 与其他 5 个认知原子的非重叠证明，边界模糊案例的归属裁决 | P2 | ≤ 400 行 | 可从非重叠性矩阵推导 |
| `GOLDEN_SET.md` | 金标准的设计依据、覆盖范围、更新历史、pass_threshold 的理由 | P1 | ≤ 300 行 | **逐原子手写** |
| `CHANGE_LOG.md` | 按版本倒序的变更记录，每条含：版本号、日期、变更描述、审批人、hash | P3 | 按需增长 | **逐原子手写** |

**机械原子**只需 `IO_CONTRACT.md` + `CHANGE_LOG.md`，不要求证据/金标准/边界文件（机械原子是确定性的）。

---

## 7. SKILL.md 正文分流策略

### 7.1 硬约束

- 总行数 ≤ 500
- 总 token 数 ≤ 5000（按 cl100k_base 近似估算）

### 7.2 分流原则

SKILL.md 正文**只保留**：
- 职责声明（1 段话）
- 核心推理流程（步骤级 SOP，不展开细节）
- "何时读取哪个 reference" 的导航规则
- 最小可用示例（1-2 个）

SKILL.md 正文**不包含**：
- 完整 schema 定义（→ IO_CONTRACT.md）
- 完整边界论证（→ BOUNDARY.md）
- 金标准样例与评分规则细节（→ GOLDEN_SET.md）
- 证据链字段语义（→ EVIDENCE_SCHEMA.md）
- 版本演进历史（→ CHANGE_LOG.md）

### 7.3 推荐正文骨架

```markdown
# [Atom Name]

## 1. 职责（Scope）
（1 段话，与 description 字段呼应但更精确）

## 2. 输入输出（Contract Summary）
（引用 IO_CONTRACT.md，此处仅列字段名速查）

## 3. 推理流程（Procedure）
1. ...
2. ...
3. ...

## 4. 边界判断（When NOT to use this atom）
（引用 BOUNDARY.md，此处仅列 2-3 条典型排除）

## 5. 证据链输出要求（Evidence Summary）
（引用 EVIDENCE_SCHEMA.md，此处仅说明"必须输出证据链"）

## 6. 示例（Minimal Example）
（1 个最小可运行示例，input → output）

## 7. 参考文件索引（References）
- IO 契约：references/IO_CONTRACT.md
- 证据链 schema：references/EVIDENCE_SCHEMA.md
- 边界证明：references/BOUNDARY.md
- 金标准：golden/GOLDEN_SET.md
- 变更日志：references/CHANGE_LOG.md
```

---

## 8. 目录结构最终形态（认知原子）

```
cognitive-atom-name/
├── SKILL.md                        # 主入口，≤500 行
├── references/
│   ├── IO_CONTRACT.md              # P2：输入输出契约
│   ├── EVIDENCE_SCHEMA.md          # P0：证据链规范
│   ├── BOUNDARY.md                 # P2：边界证明
│   └── CHANGE_LOG.md               # P3：变更记录
├── golden/                         # Synthos 专属目录
│   ├── GOLDEN_SET.md               # P1：金标准说明
│   ├── cases/                      # 测试输入集
│   └── expected/                   # 期望输出集
├── scripts/                        # 可选：辅助脚本
├── assets/                         # 可选：模板资源
└── LICENSE.txt                     # 可选
```

---

## 9. 验证流程（实施层面）

### 9.1 自动化校验（发布前必做）

每个认知原子在纳入 Synthos 前，必须通过以下校验：

1. **Agent Skills 官方校验**：`skills-ref validate ./atom-name`（规范合规性）
2. **Synthos 扩展校验**：
   - metadata 中所有必填 synthos_* 字段存在且类型正确
   - 所有 ref 字段指向的文件真实存在
   - synthos_skill_md_hash 与实际计算结果一致
   - references/ 下 5 份标准文件齐备
   - SKILL.md 正文行数和 token 数在上限内
   - allowed-tools 与 synthos_mechanical_atoms 通过架构层映射表校验一致性
   - synthos_model_version_pin 和 synthos_model_tested_on 的最近一次变更必须伴随 CHANGE_LOG.md 中对应版本的金标准通过率记录

### 9.2 人类审批（P3 要求）

自动化校验通过后，进入受控变更流程（SKILL-operations.md 将定义其细节）。本文档**不**规定人类审批的具体工具链，只规定什么字段需要审批批准。

---

## 10. 版本与演进

### 10.1 本文档自身的版本管理

SKILL-spec-profile.md 是 **Synthos 内部的元规范**，它自身的变更也遵守 P3 受控变更原则。每次修订需：
- 主版本号变更（v1 → v2）：扩展字段新增或语义变更 → **所有现存认知原子必须升级 SKILL.md**
- 次版本号变更（v1.0 → v1.1）：澄清、补充、非破坏性新增可选字段 → 现存原子可渐进升级

### 10.2 向前兼容原则

v1.0 之后的任何修改**不得**让 v1.0 已合规的原子 SKILL.md 变为不合规（除非主版本号升级）。

---

## 11. 开放问题（移交实施阶段解决）

1. **CallGraph 的物理载体**：属于 Synthos runtime，不在单个原子 SKILL.md 内。由 SKILL-architecture.md 定义。
2. **原子间调用时证据链的拼接协议**：跨原子的 evidence_chain 如何串联为完整链条，属于 runtime 层面。
3. **`skills-ref validate` 工具本身是否需要增强**以支持 Synthos 扩展字段校验：属于工具链建设，由 SKILL-operations.md 负责。
4. **模板化生成脚本** `scripts/generate_atom_references.py`：列为 SKILL-operations.md 的必须交付物。该脚本从 `atom-io-schemas.md` + 模板自动生成 IO_CONTRACT.md、EVIDENCE_SCHEMA.md、BOUNDARY.md 三份文件，减少逐原子手写成本。
