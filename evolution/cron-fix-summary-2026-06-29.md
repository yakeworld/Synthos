# Cron 修复总结 2026-06-29

## 根因

10/14 个 cron job 因 LLM 推理超时失败。三大根因：

### 1. quality-gate 技能过大（3个任务）
`unified-paper-scan`、`paper-harvester`、`paper-quality-iteration` 都引用了 quality-gate 技能。
Hermes 将完整的 SKILL.md（12KB+）注入 LLM 提示词，导致总输入超大，LLM 推理超时。

**修复**：移除 `skills=['quality-gate']` 配置，改为内联精简指令。

### 2. 链式上下文污染（3个任务）
`paper-harvester` → context_from `e75667c2351f`（literature-monitor，已失败）
`evolution-cycle` → context_from `1d9f9e01d41a`（project-library-scan，已失败）
`research-proposal-generator` → context_from `6a16d1ee7c58`（paper-harvester，已失败）

失败任务的前序输出被注入下游，膨胀上下文。

**修复**：清除 `context_from`，切断链式污染。

### 3. PubMed URL 编码问题（1个任务）
`literature-monitor` 使用了未编码的 `[Title/Abstract]`，curl 报错 exit 3。

**修复**：URL-编码为 `%5BTitle%2FAbstract%5D`。

### 4. Semantic Scholar 限流（2个任务）
`literature-monitor` 和 `daily-intelligence` 调 S2 API 无 key，返回 429。

**修复**：添加 `S2_API_KEY` 环境变量引用。

### 5. 其他超时原因
`daily-papers-report`、`project-library-scan`、`synthos-daily-promo`、`daily-intelligence` — 提示词过长 + 网络请求过多。

**修复**：精简提示词，减少 curl 请求。

## 修复后状态

| Job | 修复前 | 修复后 |
|-----|--------|--------|
| unified-paper-scan | ❌ skill注入 | ✅ 内联指令 |
| paper-harvester | ❌ skill+链式 | ✅ 精简+断链 |
| paper-quality-iteration | ❌ skill注入 | ✅ 内联指令 |
| evolution-cycle | ❌ 链式污染 | ✅ 断链 |
| research-proposal-generator | ❌ 链式污染 | ✅ 断链 |
| project-library-scan | ❌ 提示词过长 | ✅ 精简 |
| daily-papers-report | ❌ 提示词过长 | ✅ 精简 |
| literature-monitor | ❌ URL编码+S2限流 | ✅ URL编码+S2 key |
| daily-intelligence | ❌ S2限流+长提示 | ✅ S2 key+精简 |
| synthos-daily-promo | ❌ 15项超长目录 | ✅ 精简 |

## 后续建议

1. **申请 S2 API Key** — Semantic Scholar 免费限制10次/分钟，需申请 key 提高限制
2. **创建精简版 quality-gate** — 为 cron 任务创建一个仅含核心指令的版本（<2KB）
3. **避免链式 context_from** — 只链入成功任务，不链入失败任务
4. **设置 timeout 告警** — Hermes cron 缺少超时告警机制
5. **清理 cron 日志** — 2159 个日志文件，建议定期清理

## 验证

修复后所有 job 均通过检查：
- ✅ 无 quality-gate skill 注入
- ✅ 无链式 context_from 指向失败任务
- ✅ PubMed URL 已编码
- ✅ Semantic Scholar 有 API key 引用
