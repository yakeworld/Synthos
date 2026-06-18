# 远程机 NotebookLM CLI 部署配置

> 跨机器复制 NotebookLM 认证和配置的完整流程。适用场景：本地已认证可用的 NotebookLM，需要在远程服务器（work1/work2/work3）上使用相同 Google 账号。

## 核心步骤

### Step 1: 复制存储状态

```bash
# 在本地机：确认存储状态文件存在
ls -la ~/.notebooklm/profiles/<profile>/storage_state.json

# 复制到远程机
scp ~/.notebooklm/profiles/<profile>/storage_state.json \
    remote_host:~/.notebooklm/profiles/<profile>/
```

注意：只需复制 `storage_state.json`（含 cookies/认证令牌），无需复制 `config.json`（自动创建）。

### Step 2: 版本对齐 — 必须安装相同版本

```bash
# 本地查版本
notebooklm --version   # e.g. 0.4.1

# 远程机：清理旧版后安装相同版本
ssh remote_host "
    rm -f ~/.local/bin/notebooklm
    rm -rf ~/.local/share/pipx/venvs/notebooklm-py
    pipx install notebooklm-py==0.4.1
"
```

**关键**：必须 `rm -f ~/.local/bin/notebooklm` 先删旧 symlink，否则 pipx `--force` 也装不上（报 "symlink points elsewhere" warning）。

### Step 3: 处理 profile 迁移

首次在新版 CLI 上运行时，会自动将旧结构（`~/.notebooklm/browser_profile/`）迁移到新结构（`~/.notebooklm/profiles/default/`）。迁移可能因 Chrome Singleton* 锁文件失败：

```
shutil.Error: [... '/browser_profile/SingletonSocket', ... 权限拒绝]
```

**修复**：迁移前手动删除 Singleton 文件
```bash
rm -rf ~/.notebooklm/browser_profile/Singleton*
```

### Step 4: 网络连通性 — Tailscale 出口节点

远程机（CN 服务器）通常无法直连 Google。需启用 Tailscale exit node：

```bash
# 启用（需要 sudo，每台远程机执行一次）
sudo tailscale set --exit-node=<exit-node-ip>

# 验证
curl -sI --max-time 5 https://notebooklm.google.com
# → HTTP 302 说明可通
```

常见 exit node IP 见 `tailscale status | grep "exit node"`。

### Step 5: 验证（完整烟雾测试 5 步）

```bash
# 1. 检查认证状态
notebooklm profile list
# → 应显示目标 profile 为 "authenticated"

# 2. 切换到目标 profile（关键！复制 auth 后必须切换）
notebooklm profile switch <profile>
# → "Switched default profile: default → <profile>"

# 3. 再次确认默认 profile 已切换
notebooklm profile list
# → 目标 profile 前应有 * 标记

# 4. 列出笔记本（完整烟雾测试 — 同时验证 auth + 网络）
notebooklm list
# → 返回笔记本列表，而非认证错误。超时则说明网络不通。

# 5. 检查源列表（验证 RPC 功能完整）
notebooklm source list | head -5
# → 显示 source 列表。若无 output 持续 >30s，见"网络诊断"节。
```

**网络诊断**：
```
# 先确认出口节点
curl -sI --max-time 5 https://notebooklm.google.com
# HTTP 302 → 通 | 超时 → 需 exit node

# 本地能通但远程超时时，可在本地执行 notebooklm 操作
# 远程机只做 PDF 存储 + 实验计算
```

**特别说明**：即使 `profile list` 显示 "authenticated"，远程机若无法访问 Google（无 Tailscale exit node），`list` 会超时。这**不影响**本地机器正常使用 — NotebookLM CLI 只需在能连 Google 的机器上跑。

## 完整脚本（一行部署）

```bash
HOST=work3
PROFILE=ghfdshgf79
EXIT_NODE=100.65.157.17

# 1. 复制 auth
ssh $HOST "mkdir -p ~/.notebooklm/profiles/$PROFILE"
scp ~/.notebooklm/profiles/$PROFILE/storage_state.json $HOST:~/.notebooklm/profiles/$PROFILE/

# 2. 重装 CLI
ssh $HOST "
    rm -f ~/.local/bin/notebooklm
    rm -rf ~/.local/share/pipx/venvs/notebooklm-py
    pipx install notebooklm-py==0.4.1
"

# 3. 处理迁移陷阱
ssh $HOST "rm -rf ~/.notebooklm/browser_profile/Singleton*"

# 4. 切换 profile
ssh $HOST "export PATH=\$HOME/.local/bin:\$PATH && notebooklm profile switch $PROFILE"

# 5. 提示出口节点
echo "Run on remote: sudo tailscale set --exit-node=$EXIT_NODE"
echo "Then verify: ssh $HOST 'export PATH=\$HOME/.local/bin:\$PATH && notebooklm list'"
```

## 已知陷阱

| # | 陷阱 | 表现 | 修复 |
|:-:|:-----|:-----|:-----|
| 1 | 版本不匹配 | 0.3.4 无 `-p` flag / 0.6.0 无 `--profile` | 强制指定版本安装 |
| 2 | 旧 bin 占位 | pipx claim success 但 binary 指向旧 venv | 先 `rm -f ~/.local/bin/notebooklm` |
| 3 | Singleton 迁移失败 | shutil.Error: SingletonSocket | 首次运行前删除 Singleton* |
| 4 | 无出口节点 | auth 显示 authenticated 但 list 超时 | 启用 Tailscale exit node |
| 5 | storage_state 位置错 | 文件在旧路径不在 profile/ 下 | 拷贝到 `profiles/<name>/` 目录 |
| 6 | Python 版本升级后 pipx venv 断连 | `pipx install --force` 报 `FileNotFoundError: No such file or directory: '.../bin/python'` | `rm -rf ~/.local/share/pipx/venvs/notebooklm-py` 删除旧 venv 后重新 `pipx install` |
