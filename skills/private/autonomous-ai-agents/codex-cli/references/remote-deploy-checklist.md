# 远程部署检查清单

每次部署 Codex CLI 到新节点时，逐项验证：

## 验证项

- [ ] `ssh <host> "which codex && codex --version"` — 确认安装和版本
- [ ] `ssh <host> "cat ~/.codex/config.toml"` — 确认旧配置是否存在
- [ ] `ssh <host> "curl -s --connect-timeout 5 http://<vllm_ip>:8000/v1/models"` — 确认 vLLM 可达
- [ ] 拷贝 config.toml：`scp ~/.codex/config.toml <host>:~/.codex/config.toml`
- [ ] 拷贝 .env：base64 传输或 scp
- [ ] `ssh <host> "codex doctor 2>&1"` — 检查：config loaded ✓, auth env ✓, reachability ✓
- [ ] `ssh <host> "codex exec --skip-git-repo-check 'echo test' 2>&1 | head -20"` — 执行测试
- [ ] 确认输出中无 `Missing environment variable` 错误
- [ ] 确认输出中有 `model: <name>` 和 `provider: vllm`

## 常见问题速查

| 症状 | 原因 | 修复 |
|------|------|------|
| `Missing environment variable: VLLM_API_KEY` | .env 未拷贝或 .bashrc 未生效 | 检查 ~/.codex/.env 是否存在且包含 VLLM_API_KEY |
| `Not inside a trusted directory` | 不在 git 仓库 | 加 `--skip-git-repo-check` |
| `config not found` | config.toml 未拷贝 | scp ~/.codex/config.toml |
| `route exists (HTTP 404)` | vLLM endpoint 不可达 | 检查网络和防火墙 |
| `warning: Model metadata not found` | 非 OpenAI 模型 | 正常现象，忽略 |
| 环境变量在 ssh 中为空 | codex exec 不 source .bashrc | 依赖 ~/.codex/.env 而非 .bashrc |
