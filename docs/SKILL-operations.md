# SKILL-operations.md

> 地位：**流程层**。承接宪法第五/六部分的开放问题，定义受控变更、金标准维护、自动化工具链的具体操作。
> 本文档**边做边长**，不追求一次性完整。

---

## 1. 受控变更流程

### 1.1 触发条件

以下任一项触发受控变更流程（宪法P2.4 + P3.4）：

| 变更类型 | 触发条件 | 审批人 |
|---------|---------|--------|
| 新增认知原子 | 多个任务反复缺同一能力 | 人类 |
| 修改金标准 | 外部新benchmark出现 或 自设金标准发现缺陷 | 人类 |
| 原子版本升级 | 修改SKILL.md语义 或 金标准更换 | 人类 |
| 细则演化 | 不改变约束矩阵单元格含义的修改 | 人类 |

### 1.2 提案模板

存放路径：`docs/proposals/<YYYYMMDD>-<slug>.md`

```markdown
# 变更提案: <标题>

**日期**: 2026-05-XX
**提案人**: Synthos Agent / 杨晓凯
**变更类型**: 新增认知原子 / 修改金标准 / 原子版本升级 / 细则演化

## 变更描述
<1-3段话描述变更内容>

## 非重叠性证明（如是新增原子）
<与现有6个认知原子的职责边界分析>

## 影响的组件清单
- [ ] SKILL-principles.md (如涉及)
- [ ] SKILL-architecture.md
- [ ] atom-io-schemas.md
- [ ] 具体原子 SKILL.md
- [ ] core/ Python代码

## 回滚方案
<如果变更失败，如何恢复到变更前状态>

## 审批
- [ ] 人类审批
- **审批人**: 
- **审批时间**: 
- **审批意见**: 
```

### 1.3 变更日志

存放路径：`docs/change-log.md`

格式：反向时间序列表，每条记录含：日期、变更类型、影响的原子/文档、审批人。

---

## 2. 金标准维护

### 2.1 当前状态

| 原子 | golden_set_origin | cases数 | pass_threshold | 状态 |
|------|:--:|:--:|:--:|:--:|
| knowledge-extraction | self_defined | 5(框架) | 0.80 | ⬜ 待填充用例 |
| association-discovery | self_defined | 4(框架) | 0.80 | ⬜ 待填充用例 |
| hypothesis-generation | self_defined | 4(框架) | 0.80 | ⬜ 待填充用例 |
| argument-expression | self_defined | 3(框架) | 0.80 | ⬜ 待填充用例 |
| viewpoint-verification | self_defined | 4(框架) | 0.80 | ⬜ 待填充用例 |
| task-router | self_defined | 5(框架) | 1.00 | ⬜ 待填充用例 |

### 2.2 金标准用例格式

```
golden/cases/case_NNN.json    ← 输入（模拟上游原子输出）
golden/expected/case_NNN.json ← 期望输出（用于比对）
```

每条case记录在GOLDEN_SET.md中，含：case编号、测试维度、输入摘要、期望摘要。

### 2.3 金标准更新流程

1. 外部新benchmark出现 → Agent检索并提案
2. 自设金标准发现缺陷（某case导致误判）→ Agent提案修订
3. 人类审批 → 更新golden/文件 → 更新GOLDEN_SET.md → 重跑测试 → 更新pass_threshold → 升级原子版本

### 2.4 金标准扫描周期

- **每周**: Agent检索arXiv/PubMed是否有新的ADHD相关benchmark
- **每月**: 人工review金标准的覆盖充分性
- **按需**: 原子修改后立即重跑金标准

---

## 3. 自动化工具链

### 3.1 已有工具

| 工具 | 路径 | 用途 |
|------|------|------|
| 原子1搜索+下载 | `core/atoms/atom1_knowledge_acquisition.py` | 多源检索+PDF下载 |
| Pipeline编排 | `core/atom_pipeline.py` | 路由→机械→认知全链 |
| SHA-256哈希 | `<PENDING>`占位符算法 | SKILL.md指纹计算 |

### 3.2 待建工具

| 工具 | 优先级 | 用途 |
|------|:--:|------|
| `scripts/generate_atom_references.py` | P2 | 从atom-io-schemas.md模板化生成IO_CONTRACT/EVIDENCE_SCHEMA/BOUNDARY |
| `scripts/validate_skill.py` | P2 | 校验单个SKILL.md的spec-profile合规性 |
| `scripts/run_golden_test.py` | P1 | 对单个原子执行金标准测试，输出通过率 |
| `scripts/pmid_to_pmcid.py` | P3 | PMID→PMCID转换（修复PMC下载） |

### 3.3 日常运维命令

```bash
# 运行全链
python3 run_pipeline.py run 'ADHD eye-tracking diagnosis'

# 查看状态
python3 run_pipeline.py status

# 组装输出
python3 run_pipeline.py assemble <run_id>

# 单独搜索+下载
python3 -c "
from core.atoms.atom1_knowledge_acquisition import Atom1KnowledgeAcquisition
Atom1KnowledgeAcquisition().run({'query':'...','max_results':10})
"
```

---

## 4. 模型版本管理

### 4.1 当前绑定

所有认知原子的 `synthos_model_version_pin` = `"deepseek/deepseek-v4-pro@2026-05-10"`

### 4.2 模型切换流程

1. Agent检测到新模型可用
2. 提案："切换到 <new_model>，重跑全部金标准"
3. 人类审批
4. 逐原子：重跑金标准 → 记录通过率 → 更新 model_version_pin + model_tested_on
5. 更新 CHANGE_LOG.md
6. 若通过率下降 >5%，回滚并标记风险

---

## 5. S2 API Key 管理

- 当前状态：403 Forbidden（key过期）
- fallback：PubMed + arXiv正常工作
- 更新路径：https://www.semanticscholar.org/product/api#api-key-form
- 更新后：设置环境变量 `SEMANTIC_SCHOLAR_API_KEY`，无需改代码

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2026-05-10 | 初始版本：受控变更流程、金标准维护规范、工具链清单 |
