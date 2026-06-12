# Cron Structural Audit — Cron 轮次探测记录

**记录**: Cron 轮次 vs Human-invoked Cycle 探测结果的不一致

## 背景

Cycle 68（人类/CLI 触发）报告了过于乐观的 7 原子结构检查结果：
- research-ideation 标记为 3/3 PASS（实际 0/3）
- 6/7 原子被认为有 signature（实际 1/7）
- 2/7 原子被认为有 IO_CONTRACT（实际 1/7）

2026-06-09 Cron 轮次使用严格 regex 检测，给出了真实读数：
- 仅 knowledge-acquisition 通过全部 3 项（version + signature + IO_CONTRACT）
- 仅 argument-expression 有 signature
- 仅 knowledge-acquisition 有 IO_CONTRACT
- 结构分从 0.29 修正为 0.4（按属性计数 8/21）

## 原因分析

Cycle 68 的探针检测逻辑较为宽松：
1. `name:` 在 frontmatter 中出现就被计为 signature（过于宽泛）
2. 路径检查假设所有原子在 `skills/<atom>/SKILL.md`（漏掉了 research-ideation 的嵌套位置）
3. 对 IO_CONTRACT 的检测未覆盖所有变体

Cron 轮次的检测逻辑更严格：
1. signature 需独立的 `signature` 声明或 `name:` + `signature:` 组合
2. 路径通过 `os.path.exists()` 确认
3. IO_CONTRACT 通过明确标题和关键词匹配

## 教训

1. **人类触发的轮次可能过于乐观**：检测逻辑可能不够严格
2. **Cron 轮次是 ground truth**：严格检测的结果更可靠
3. **per-atom 结果不应被信任**：即使同一周期，不同检测逻辑产生不同结果
4. **检测代码应标准化**：PROBE 技能应固化严格的检测规则
