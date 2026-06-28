# SkillOpt 吸收记录 — 微软 AI Agent 技能自动优化

## 日期
2026-06-28 (Cycle 184)

## 来源
https://github.com/microsoft/SkillOpt

## 核心吸收点

### 1. Diff-Based 增量修改

SkillOpt 不整体重写 skill 文件，而是：
1. 识别失败相关的指令部分
2. 只修改这些部分
3. 保留已验证正确的部分

**Synthos 验证**：修改 `hermes-agent/SKILL.md` 时，只影响了"浏览器工具排障"部分，
"飞书ID格式区分"和"send_message工具限制"部分完全未动。
验证方法：`skill_view` 读取后确认其他部分未改动。

### 2. 四段式结构化

SkillOpt 要求 skill 包含：
- **Description**: 技能做什么
- **Instructions**: 具体怎么做（步骤化）
- **Constraints**: 约束条件
- **Examples**: 示例输入输出

**Synthos 验证**：创建 `pubmed-search-basic` 使用四段式，API 调用通过。
四段式不是必须的（已有技能用自由格式），但新技能建议遵循。

### 3. 失败→自动优化链路

SkillOpt 的核心创新：失败自动触发优化，不需要人工发现+人工要求修改。

**当前 Synthos 状态**：需要人工发现问题 → 人工要求修改 skill。
**目标状态**：质量门检测到 skill 问题 → 自动触发 skill 优化循环。

**这是目前最缺的环节**，需要在后续周期优先补上。

## 吸收方法

1. 阅读 SkillOpt 文档和代码
2. 提取核心方法论（不是具体实现）
3. 与 Synthos 现有能力对比
4. 确定哪些直接复用、哪些需要改造
5. 实际测试验证（创建测试技能 + 执行操作）
6. 记录吸收过程和验证结果

## 结论

SkillOpt 的三条核心机制（diff-based、四段式、自动优化）大部分已被 Synthos 吸收或具备雏形。
最缺的是第 3 条——失败→自动优化的自动化链路。
