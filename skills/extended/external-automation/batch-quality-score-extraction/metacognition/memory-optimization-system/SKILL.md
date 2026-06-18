---
name: memory-optimization-system
description: 记忆系统全面优化：上下文卸载(Mermaid压缩)、FSRS巩固cron(凌晨3点)、memory↔fact_store桥接、去重与清理。覆盖TencentDB
version: 1.0.0
  Agent Memory四层架构缺口。
allowed-tools: memory fact_store terminal write_file read_file cronjob process
metadata:
  synthos:
    author: Hermes Agent
    signature: 'input: dict -> output: dict'
    related_skills:
    - conversation-to-memory
    - memory-enhancement
    - quality-gate
    - post-compile-dual-quality-check
    priority: P0
    version: 1.0.0
    execution_rule: 本技能在会话中持续生效。使用以下自动规则： (1) 工具输出>10KB → 建议卸载到 context_refs/*.md
      (2) 会话结束前 memory 超 90% → 建议清理 (3) 发现 memory ↔ fact_store 重复 → 合并 (4) 复杂任务结束
      → 运行 consolidation 检查

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

## 已部署组件

| 组件 | 脚本 | Cron | 模式 |
|:-----|:-----|:----:|:----:|
| **QC批量扫描** | `qc_batch_scan.py` | 每6h | no_agent |
| **记忆巩固** | `memory_consolidate.py` | 每天3:00 | no_agent |
| **上下文卸载** | 本skill（工作流） | 无cron | 会话内 |

## 1. 上下文卸载（Mermaid压缩）

### 触发条件

当任何工具输出超过 **10KB** 或 **50行** 时：

```
长输出 → [自动检测]
  ├── 保存原文到 ~/.hermes/context_refs/{hash}.md
  └── 替换为 Mermaid 摘要（保持上下文轻量）
```

### Mermaid 摘要模板

````markdown
<details>
<summary>📄 长输出摘要：{命令简述}</summary>

```mermaid
graph LR
    CMD["{命令}"] --> OUT["{输出大小}"]
    OUT --> KEY1["{关键信息1}"]
    OUT --> KEY2["{关键信息2}"]
```

📎 全文: `~/.hermes/context_refs/{hash}.md`
</details>
````

### 实际工作流

```bash
# 1. 当检测到长输出时，自动执行:
mkdir -p ~/.hermes/context_refs/

# 2. 保存原文（terminal 的输出被管道捕获）
# 在 terminal() 后，用 execute_code 判断输出长度
# 如果 > 10KB，自动执行:

# 3. 在回复中只用摘要 + 引用路径
# 用户想看细节时: read_file ~/.hermes/context_refs/{hash}.md
```

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

# 输出示例:
# 🧠 [mem-consolidate] 05-30 03:00 — 首次巩固
#     Memory: 2,149/2,200 (98%)
#     Fact Store: 53 facts
#     建议: memory 空间 98% — 需清理
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
    """返回条目的记忆健康度评级"""
    R = 1.0 / (1.0 + entry_age_days / (9.0 * 2.5))  # 假设 S=2.5天
    if access_count == 0 and entry_age_days > 14:
        return "🟫 可移除 — 从未访问且超过2周"
    if R < 0.3:
        return "🟨 低可检索 — 建议移出 memory 或降低优先级"
    if R > 0.7 and access_count >= 2:
        return "🟢 健康 — 频繁使用"
    return "🟩 正常"
```

## 3. Memory ↔ Fact Store 桥接

### 提升规则

```
memory 空间 > 90% → 扫描可提升到 fact_store 的条目
  条件:
  - 含明确实体名（方法/工具/人）→ 适合 fact_store
  - 跨session有效 → 适合 fact_store
  - 仅在当前 session 有用 → 留在 memory 或删除
  
fact_store → memory:
  - fact_store 中 trust_score > 0.7 且 retrieval_count > 2 → 确保在 memory 中有提及
  - 条件: 当前 memory 空间 < 80%
```

### 去重规则

```
memory 和 fact_store 中内容相似度 > 80% 的条目：
  1. 以 fact_store 版本为准（有信任评分）
  2. 压缩 memory 中对应的冗余条目
  3. 记录合并日志到 memory 的合并字段
```

## 4. 会话内记忆管理检查清单

每次复杂任务（5+ 工具调用）后：

- [ ] memory 使用量 check: >90% 触发清理
- [ ] 是否有新的用户偏好/环境细节可保存
- [ ] 是否有过期条目（项目状态变化、PR已合并）可替换
- [ ] 长工具输出是否已卸载到 context_refs/
- [ ] fact_store 是否有新事实可添加

## 5. 自动化铁律（用户明确 2026-06-04）

> **记忆管理必须是自动的，不应等待用户提醒。** 用户说"记忆整理不应该是自动化的吗？" — 这是偏好信号，非功能请求。

### 执行规则

| 条件 | 行动 |
|:-----|:------|
| memory 空间 > 85% | 本次会话�\n\n---\n*详细内容已移至 references/ 目录。*
