# Cycle 183 Delegation Pattern — 后台派发进化周期

> 发现日期：2026-06-28。通过 `delegate_task(background=true)` 将进化周期完整流程委托给子代理，实现"派发即离开"模式。

## 核心模式

```
Hermes Agent (本会话)
  ├── delegate_task(background=true)
  │     ├── 完整上下文注入（状态、目录、铁律、执行流程）
  │     ├── toolsets: ["terminal", "file"]
  │     └── 子代理独立运行 → 完成后自动返回结果
  │
  └── 本会话立即结束，用户可继续其他工作
```

## 关键设计决策

### 1. 完整上下文注入

子代理没有对话历史，所以必须在一个 `context` 字段中注入：
- 当前进化状态（cycle, score, status, next_actions）
- 工作目录和关键路径
- 工具安装状态（Codex CLI 版本、配置）
- tmux 会话状态
- **所有 10 条进化铁律**（从 evolution 技能的陷阱章节提取）

### 2. 执行流程标准化

将进化流程抽象为可重用的任务描述模板：

```
Phase 1: DIAGNOSE — 运行 diagnose.py，获取六维评分
Phase 2: OPTIMIZE — 根据诊断结果选择最高 ROI 改进
Phase 3: OPTIMIZE 执行 — 代码/技能级改进
Phase 4: VERIFY — 重新计算分数确认提升
Phase 5: CRYSTALLIZE — 更新 state.json + evolution-log + git commit
```

### 3. 铁律清单化

将 evolution 技能中的 10+ 个陷阱压缩为执行约束列表，直接注入子代理的 prompt：

1. 诊断必须先跑（运行 diagnose.py）
2. 六维公式必须精确计算
3. BENCHMARK 必须从零重算
4. Git Add -A 连坐陷阱
5. 前缀键陷阱
6. 脏文件检查
7. JSON 编辑陷阱
8. 技能路径陷阱
9. Git 结构债务
10. 原子路径验证

### 4. 约束条件明确

- EDIT_BUDGET: 最多修改 3 个文件
- 连续 3 轮无进展 → 降级探索模式
- 相同目标连续 2 次 → 自动切换维度
- score 提升 < 0.01 → 视为收敛

## 适用场景

这个模式适用于所有需要长时间运行、多步骤、有严格约束的自动化任务：

1. **进化周期** — DIAGNOSE → OPTIMIZE → VERIFY → CRYSTALLIZE
2. **大规模技能审计** — 扫描 191 个 SKILL.md，识别问题
3. **技能合并/迁移** — 多文件操作，需要 git 同步
4. **代码重构** — 多步骤、需要验证

## 陷阱与注意事项

1. **子代理无法使用 `execute_code`**（cron 模式下被 BLOCKED）→ 改用 `terminal()` heredoc
2. **子代理没有对话上下文** → 所有信息必须一次注入完整
3. **子代理无法交互式确认** → 所有决策必须预先定义规则
4. **完成后自动返回结果** → 设计时考虑结果格式，确保可解析

## 效果

- 本会话：Hermes 在 1 条消息内完成派发，用户立即获得反馈
- 子代理：独立运行，不受本会话上下文污染
- 结果：完整进化周期报告自动进入对话
