# Cron 配置与管理

## 基础命令

```bash
# 创建
hermes cron create \
  --name "job-name" \
  --prompt "## Task prompt..." \
  --schedule "0 */3 * * *" \      # cron 表达式
  --repeat forever \
  --deliver origin

# 列表
hermes cron list

# 更新
hermes cron update JOB_ID --deliver feishu:yake_local
hermes cron update JOB_ID --model '{"model":"qwen3.6-35b-nvfp4","provider":"custom:amax"}'

# 删除
hermes cron remove JOB_ID
```

## 模型/Provider 配置

### 关键规则

| 配置 | 效果 |
|:-----|:-----|
| `model: null, provider: null` | 继承全局默认模型 |
| `model: qwen..., provider: deepseek` | ❌ 模型名对但 provider 指向付费 API → **空耗费用** |
| `model: qwen..., provider: custom:amax` | ✅ 明确走本地 |
| 创建时未指定 | 后续 update 可加 `--model` 参数 |

### 迁移示例

```bash
# 检查当前 job 的模型
hermes cron list | grep -E "model|provider"

# 批量切到本地（逐个 job）
hermes cron update JOB_ID \
  --model '{"model":"qwen3.6-35b-nvfp4","provider":"custom:amax"}'
```

## 投递配置

- `deliver: "origin"` → 固化创建时的 receive_id。**渠道变更（新飞书群、重装等）后失效**，投递报错 `invalid receive_id`
- 显式指定会重新解析：`deliver: feishu:yake_local`
- 脚本类（`no_agent: true`）用 `deliver: local`
- `deliver: local` 不投递到聊天，仅存本地日志

### 修复投递错误

```bash
# 错误：Feishu send failed: invalid receive_id
# 原因：deliver: origin 指向旧 receive_id
# 修复：更新为目标渠道
hermes cron update JOB_ID --deliver feishu:yake_local
```

## ⚠️ 关键陷阱

### 1. memory 工具在 cron 模式不可用
cron 环境无持久化 memory 存储。任何依赖 `memory` 工具的 cron job 都会返回 "Memory is not available in this environment"。**这不是配置问题，是架构限制。**

解决方案：
- 移除此类 cron job（它永远无法正常工作）
- 需要异步记忆操作 → 用 no_agent 脚本 + 文件读写替代

### 2. 默认模型变更影响所有 model:null job
更改 `config.yaml` 的 `model.default` 后，所有 `model: null` 的 cron job 自动跟随。确保变更前知晓影响范围。

### 3. 创建时 model 参数不是字符串
`--model` 参数接收 JSON 字符串：
```bash
# ✅ 正确
--model '{"model":"qwen3.6-35b-nvfp4","provider":"custom:amax"}'
# ❌ 错误
--model "qwen3.6-35b-nvfp4"
```

### 4. last_delivery_error 不清空
更新 deliver 后，旧错误日志保留（显示上次失败）。不影响后续运行，属于正常现象。

## 模式参考

| Job 类型 | 推荐 deliver | 推荐 model |
|:---------|:------------|:-----------|
| 科研探索（长时间） | `origin` (feishu) | 本地 qwen |
| 脚本同步（rclone） | `local` | N/A (no_agent) |
| 报告生成 | `origin` (feishu) | 本地 qwen |
| 需要高推理质量 | 可临时切 DeepSeek | `deepseek-v4-flash` |
