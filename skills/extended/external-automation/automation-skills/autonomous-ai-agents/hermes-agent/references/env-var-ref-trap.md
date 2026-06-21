# .env 环境变量引用陷阱

## 现象

config.yaml 中 `providers.<name>.api_key` 写为纯字符串如 `DEEPSEEK_API_KEY`，Hermes 不自动解析为 `.env` 中的实际值。导致 API 调用静默失败或 fallback 到错误 provider。

## 根因

Hermes config loader 的 `_expand_env_vars()` 函数（`config.py:5300`）使用正则 `r"\$\{([^}]+)}"` 只展开 `${VAR}` 格式的环境变量引用。裸字符串 `DEEPSEEK_API_KEY` 被当作字面值处理，不会从 `os.environ`（由 `load_hermes_dotenv()` 从 `.env` 加载）中解析。

## 修复

所有 config.yaml 中引用 `.env` 变量的 `api_key` 必须使用 `${VAR}` 包裹：

```yaml
# ❌ 错误 — 字面字符串，不展开
providers:
  deepseek:
    api_key: DEEPSEEK_API_KEY

# ✅ 正确 — ${} 包裹，被 _expand_env_vars 展开
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
```

## 诊断步骤

```bash
# 1. 确认 .env 中有真实 key（非 *** 占位符）
grep 'DEEPSEEK_API_KEY' ~/.hermes/.env

# 2. 确认 config.yaml 中用 ${} 包裹
grep 'api_key.*DEEPSEEK' ~/.hermes/config.yaml
# 应输出: api_key: ${DEEPSEEK_API_KEY}

# 3. 验证 API 连通
curl -s --max-time 10 https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"OK"}],"max_tokens":5}'

# 4. 检查 gateway 进程是否有该环境变量
# 注意: systemd service 进程可能没有，因为 Python 内部 load_hermes_dotenv() 的
# os.environ 修改在 systemd clean environment 下可能不反映到 /proc/PID/environ
# 这不影响运行时行为，因为 config loader 在 Python 内部完成展开

# 5. 用 hermes doctor 确认 provider 状态
hermes doctor | grep -i deep

# 6. 修改后重启 gateway
# systemd: systemctl --user restart hermes-gateway.service
# 手动: kill 后重新启动
```

## 已影响的配置

- `~/.hermes/config.yaml` L9: `providers.deepseek.api_key` 已从 `DEEPSEEK_API_KEY` 改为 `${DEEPSEEK_API_KEY}`
- 时间: 2026-06-21

## 排查要点

1. **不要依赖 shell 环境变量检查**。`echo $DEEPSEEK_API_KEY` 在 shell 中为空不代表 key 没配置 — Hermes 从 `.env` 文件解析，不依赖 shell export。
2. **systemd service 的环境变量不继承 `.env`**。systemd `hermes-gateway.service` 没有 `EnvironmentFile` 指令，Python 进程内的 `load_hermes_dotenv()` 才是正确加载路径。`/proc/PID/environ` 中可能看不到 `.env` 变量（取决于 systemd 隔离级别）。
3. **`hermes doctor` 是权威验证**。它加载 config 并实际测试 API 连通性。
