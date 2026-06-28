# Cron Provider 超时修复模式

## 问题

cron 任务用 `custom:amax` provider + `qwen3.6-35b-nvfp4` 模型，prompt 过长（完整模板+多步骤指令），LLM 处理超时 → `RuntimeError: Request timed out`。

## 根因

prompt 过长 → LLM 处理时间超出 provider 超时限制。

## 修复步骤

1. `cronjob(action='list')` 获取所有 job 列表
2. 筛选 `last_status == "error"` 的 job（排除 no_agent 任务）
3. 读取最近错误日志：`~/.hermes/cron/output/<job_id>/*.md`
4. 确认错误是 `Request timed out`
5. 精简每个 job 的 prompt：
   - 去掉冗长模板
   - 限定输出 ≤200 字
   - 增加 `[SILENT]` 触发条件
   - 保留核心 bash 命令
6. `cronjob(action='update', job_id=..., prompt=新prompt)` 更新

## 关键原则

- 每个 job 独立修复
- 保留 `[SILENT]` 出口
- 限定输出字数
- bash 命令前置，LLM 只负责判断和格式化
- 10 个 job 可一次性批量更新
