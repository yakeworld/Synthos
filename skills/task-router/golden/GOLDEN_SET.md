# GOLDEN_SET.md — task-router

> 对应原则：P1
> golden_set_origin: self_defined

## 设计依据

路由器的金标准测试最简单——输入是 query 字符串，输出是确定的（complexity + atom_chain）。关键在于验证：**给定明确的触发词，路由器是否输出正确的结果**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 四种复杂度 | 4/4 | simple, medium, complex, full |
| 中英文混合 | 3/5 | 中文、英文、中英混合 |
| 边缘案例 | 2 | 无关键词（默认medium）、歧义查询 |

## 测试用例

### case_001: 英文简单搜索
- **输入**: `"find papers about ADHD eye-tracking"`
- **期望**: complexity=`simple`, chain=`[knowledge-acquisition]`

### case_002: 中文分析查询
- **输入**: `"帮我分析ADHD眼动追踪领域的研究现状"`
- **期望**: complexity=`medium`, chain=`[1,2,3]`

### case_003: 英文写作查询
- **输入**: `"write a survey on ADHD biomarkers"`
- **期望**: complexity=`complex`, chain=`[1,2,3,4,5]`

### case_004: 中文验证查询
- **输入**: `"评估我这个假设的鲁棒性"`
- **期望**: complexity=`full`, chain=`[1,2,3,4,5,6]`

### case_005: 无关键词（默认）
- **输入**: `"ADHD eye-tracking"`
- **期望**: complexity=`medium`, chain=`[1,2,3]` (默认)

### case_006: 空字符串（边缘）
- **输入**: `""`
- **期望**: complexity=`simple` or `medium`, chain=`[knowledge-acquisition]` (最短回退链)

### case_007: Unicode 查询（非 ASCII）
- **输入**: `"🔬 科学发现 → 假说验证 🧪"`
- **期望**: complexity=`full` or `complex`, chain=`[1,2,3,4,5,6]` (emoji+unicode 应触发全链)

## pass_threshold: 1.0

路由器的判定是**确定性规则**（关键词匹配），不是推理过程。因此 pass_threshold 设为 1.0——所有 7 个 case 必须完全正确。

### 阈值理由
- 路由错误会系统性影响下游所有原子的调用（错误传播）
- 规则是显式的关键词匹配，不存在合理的语义变异空间
- 如果某条规则需要修改，应通过 P3 受控变更流程修改 SKILL.md 而非容忍"部分正确"

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，5 个 case | Synthos Agent |
