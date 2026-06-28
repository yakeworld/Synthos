---
name: memory-optimization-system
description: 记忆系统全面优化：上下文卸载(Mermaid压缩)、FSRS巩固cron(凌晨3点)、memory↔fact_store桥接、去重与清理、hidden Unicode字符处理。覆盖TencentDB
version: 1.1.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: directory-index
    description: "Directory index for memory-optimization-system"
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills:
    - conversation-to-memory
    - quality-gate
    priority: P2

---
> **注意**: 本技能是记忆管理的唯一入口。`memory-enhancement` 已合并至此。

---
# 记忆系统全面优化

> **记非日记，长养为要。散则聚之，独则连之。**

## IO_CONTRACT

- **input**: `context_size: int` — 当前会话上下文大小（bytes/lines）
- **input**: `memory_entries: list[dict]` — memory + fact_store 快照
- **input**: `consolidation_trigger: str` — 触发类型（qc_scan / cron_consolidation / context_overflow / session_end）
- **output**: `optimization_report: dict` — 优化结果（offloaded: list, merged: list, cleaned: list）
- **output**: `context_refs: list[str]` — 卸载的 context_refs/*.md 路径
- **output**: `metrics: dict` — 优化前后内存使用对比
> 对应原则：P2（机械原子暴露输入输出规范）
## 已部署组件

| 组件 | 脚本 | Cron | 模式 |
|:-----|:-----|:----:|:----:|
| **QC批量扫描** | `qc_batch_scan.py` | 每6h | no_agent |
| **记忆巩固** | `memory_consolidate.py` | 每天3:00 | no_agent |
| **上下文卸载** | 本skill（工作流） | 无cron | 会话内 |

## 1. 上下文卸载（Mermaid压缩）

### 触发条件

当任何工具输出超过 **10KB** 或 **50行** 时：

长输出 → [自动检测]
  ├── 保存原文到 ~/.hermes/context_refs/{hash}.md
  └── 替换为 Mermaid 摘要（保持上下文轻量）

### 实际工作流

1. 当检测到长输出时，自动执行: mkdir -p ~/.hermes/context_refs/
2. 保存原文（terminal 的输出被管道捕获）
3. 在回复中只用摘要 + 引用路径
4. 用户想看细节时: read_file ~/.hermes/context_refs/{hash}.md

### 卸载级别

| 级别 | 触发条件 | 行为 |
|:----:|:---------|:-----|
| L1 | 输出 > 10KB | 保存原文 + Mermaid摘要 |
| L2 | 输出 > 50KB | 只保存，回复中仅写"已保存到 {path}" |
| L3 | 命令行交互输出 | 只保存关键结果行 |

## 2. 记忆巩固（Cron每天凌晨3点）

### 运行脚本

```bash
# 手动触发
python3 ~/.hermes/scripts/memory_consolidate.py
```

### Cron 配置

```jsonc
// 已在 cron 注册:
{
  "job_id": "9926ae23cdbc",
  "name": "memory-consolidation",
  "schedule": "0 3 * * *",
  "script": "memory_consolidate.py",
  "no_agent": true
}
```

### FSRS 评估逻辑（用于会话内手动评估记忆条目）

```python
# 快速计算
def memory_health(entry_age_days, access_count):
    R = 1.0 / (1.0 + entry_age_days / (9.0 * 2.5))  # 假设 S=2.5天
    if access_count == 0 and entry_age_days > 14:
        return "可移除 — 从未访问且超过2周"
    if R < 0.3:
        return "低可检索 — 建议移出 memory 或降低优先级"
    if R > 0.7 and access_count >= 2:
        return "健康 — 频繁使用"
    return "正常"
```

## 3. Memory ↔ Fact Store 桥接

### 提升规则

memory 空间 > 90% → 扫描可提升到 fact_store 的条目
  条件:
  - 含明确实体名（方法/工具/人）→ 适合 fact_store
  - 跨session有效 → 适合 fact_store
  - 仅在当前 session 有用 → 留在 memory 或删除

fact_store → memory:
  - fact_store 中 trust_score > 0.7 且 retrieval_count > 2 → 确保在 memory 中有提及
  - 条件: 当前 memory 空间 < 80%

### 去重规则

memory 和 fact_store 中内容相似度 > 80% 的条目：
  1. 以 fact_store 版本为准（有信任评分）
  2. 压缩 memory 中对应的冗余条目
  3. 记录合并日志到 memory 的合并字段

## 4. 会话内记忆管理检查清单

每次复杂任务（5+ 工具调用）后：

- [ ] memory 使用量 check: >90% 触发清理
- [ ] 是否有新的用户偏好/环境细节可保存
- [ ] 是否有过期条目（项目状态变化、PR已合并）可替换
- [ ] 长工具输出是否已卸载到 context_refs/
- [ ] fact_store 是否有新事实可添加

## 5. 自动化铁律

记忆管理必须是自动的，不应等待用户提醒。

### 执行规则

| 条件 | 行动 |
|:-----|:------|
| memory 空间 > 85% | 本次会话主动清理 |
| memory 空间 > 90% | 立即清理 + 压缩 |
| memory 空间 > 95% | 强制清理至 < 70% |

## 6. 陷阱：hidden Unicode 字符导致 memory remove/replace 静默失败

**症状**: `memory` 工具的 `remove` 和 `replace` action 使用 `old_text` 做精确字符串匹配。如果已存储的条目中包含不可见 Unicode 字符（如零宽空格 U+200B、箭头变体 U+2192→ vs U+2197↗ 等），匹配会失败，不报错、不提示、无任何输出。

**根因**: 用户的历史条目通过不同来源/输入法/工具链创建，某些字符被不可见地替换。如 `→`（U+2192 ARROW）在某些终端显示不同，或直接混入零宽空格（U+200B）。

**修复方案**:

1. 使用 remove 时，old_text 只取前 3-5 个 ASCII 字符（短而唯一）
   - ✅ `memory(action='remove', old_text='核心哲学')`
   - ❌ `memory(action='remove', old_text='核心哲学: Synthos自进化为唯一目标...')`

2. 如果 remove 静默失败（无输出），先用 add 写干净版本，再短前缀 remove 旧版本

3. 清理后务必做空间自检：查看 memory 输出，确认释放了预期空间

4. fact_store 同理 — 删除条目时 trust_score 低且 retrieval_count=0 的条目优先清理

5. 验证: 每次 remove 后，确认 memory 输出中的 `capacity: X/2200` 数字变化。如果不变，说明 old_text 匹配失败。

---
*详细内容已移至 references/ 目录。*

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
