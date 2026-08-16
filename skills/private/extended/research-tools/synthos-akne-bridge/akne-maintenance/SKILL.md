---
name: akne-maintenance
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'akne-maintenance -> synthos-akne-bridge: synthetic skill for akne maintenance'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
    signature: 'akne-maintenance -> synthos-akne-bridge: synthetic skill for akne maintenance'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: AKNE 系统状态（图谱目录、源文件、守护进程）— 待诊断/维护的对象
- **input**: 运维操作请求 — 日常检查、修复、审计类型
- **output**: 16项综合健康审计结果 — 连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式等指标
- **output**: 审计报告（五阶段：健康诊断→内容矛盾→研究空白→假设→修复）

## 原则 (Principles)

- **一次尽测**：`akne-comprehensive-audit.py` 一次运行覆盖 16 项指标，分而测之则互验失据。
- **五阶递进**：审计必循健康诊断→内容矛盾→研究空白→假设→修复之序，次序不乱则脉络清晰。
- **矛盾先于假设**：内容矛盾未明，则假设无据；先立矛盾之实，后生假设之理。
- **路径去冗**：符号链接（如 /home/... 与 /media/...）虽同 inode，仍须归一，避免重名与命名空间之混。

|
| `references/operations-reference.md` | 运维操作速查 — 日常检查、修复、守护进程、常见问题速查表 |
| `references/audit-report-template.md` | 全面审计报告模板 — 五阶段结构（健康诊断→内容矛盾→研究空白→假设→修复） |
| `references/path-redundancy-2026-06-18.md` | 路径冗余诊断 — /home/yakeworld/Synthos 是 /media/.../Synthos 的符号链接，inode相同 |
| `scripts/akne-comprehensive-audit.py` | 16项综合健康审计脚本 — 一次运行覆盖连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式/元数据/Wiki污染/entity命名空间/路径前缀等全部指标 |


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[AKNE-001]** 执行健康审计时 → 必须使用综合脚本一次性覆盖全部 16 项指标，禁止分项测试以确保证据互验
- **[AKNE-002]** 生成审计报告时 → 严格遵循“健康诊断→内容矛盾→研究空白→假设→修复”的五阶递进顺序
- **[AKNE-003]** 处理内容冲突时 → 优先确认并解决内容矛盾，仅在矛盾明确后方可生成假设
- **[AKNE-004]** 处理路径冗余时 → 识别并归一化指向同一 inode 的符号链接（如 /home 与 /media），消除命名空间混淆
- **[AKNE-005]** 接收运维请求时 → 首先验证输入参数、文件及路径的完整性与有效性
- **[AKNE-006]** 执行异常操作时 → 确保错误信息包含具体上下文及恢复建议，并拒绝执行未验证的代码

## 验证清单 · VERIFICATION

- [ ] 一次尽测（AKNE-001）：健康审计是否用 `akne-comprehensive-audit.py` 一次性覆盖全部 16 项指标，未分项测试
- [ ] 指标齐全：连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式等 16 项是否均有可溯数值
- [ ] 五阶递进（AKNE-002）：审计报告是否严格循"健康诊断→内容矛盾→研究空白→假设→修复"次序
- [ ] 矛盾先于假设（AKNE-003）：内容矛盾是否在生成假设之前确认解决，无"先假设后矛盾"倒序
- [ ] 路径去冗（AKNE-004）：同 inode 符号链接（/home 与 /media）是否已归一，无重名与命名空间混淆
- [ ] 输入校验（AKNE-005）：图谱目录、源文件、守护进程等输入是否先验证完整性与有效性
- [ ] 安全护栏（AKNE-006）：错误信息是否含具体上下文与恢复建议，且拒绝执行未验证的代码

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 一个验证过路径存在、可读的 AKNE 图谱目录 + 源文件（先按 AKNE-005 校验输入完整性/有效性），作为 `akne-comprehensive-audit.py` 的一次尽测输入。
- **Golden Output**: 一次运行产出 16 项指标（连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式等）均有可溯数值，并按"健康诊断→内容矛盾→研究空白→假设→修复"五阶递进（AKNE-001/002）生成审计报告。
- **Golden Error**: 收到不存在的图谱目录或无效运维请求 → 预期错误信息含具体上下文与恢复建议（建议的路径修正或参数补全），并拒绝执行未验证的代码（AKNE-005/006）。

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## 示例 · EXAMPLES

**示例 1 · 日常健康检查**
- 输入：AKNE 图谱目录 + 源文件（先按 AKNE-005 验证路径存在、可读）
- 操作/输出：运行 `scripts/akne-comprehensive-audit.py` 一次尽测（AKNE-001），得到 16 项指标（连通性/孤立节点/重名/自环/源文件覆盖/向量/边格式等）
- 验证：16 项指标均有可溯数值，未分项测试，通过"一次尽测"与"指标齐全"两条清单

**示例 2 · 五阶递进审计报告**
- 输入：一次审计发现 2 处实体内容矛盾
- 操作/输出：按 AKNE-002 次序产出报告——健康诊断 → 内容矛盾 → 研究空白 → 假设 → 修复；矛盾解决后（AKNE-003）才生成假设
- 验证：检查报告章节顺序无"先假设后矛盾"倒序，通过 AKNE-002/003 清单项

**示例 3 · 路径冗余修复**
- 输入：审计发现 /home/yakeworld/Synthos 与 /media/.../Synthos 同 inode 重复入图（见 references/path-redundancy-2026-06-18.md）
- 操作/输出：按 AKNE-004 归一为单一前缀，消除重名与命名空间混淆
- 验证：复跑综合审计，"重名/路径前缀"指标归零；错误信息若出现则含上下文与恢复建议（AKNE-006）
