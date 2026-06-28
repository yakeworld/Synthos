---
name: linux-environment-troubleshoot
description: "Linux 环境诊断与修复 — Python venv 隔离、LaTeX/MiKTeX、Playwright 浏览器、dpkg 修复。覆盖常见环境故障的根因诊断与修复。"
metadata:
  synthos:
    priority: P2
    atom_type: class-level
    description: "Linux 环境诊断与修复 — 覆盖 Python 虚拟环境、LaTeX 编译、Playwright 浏览器、dpkg/apt 修复。"
    signature: 'linux-env -> python-venv + latex + playwright + system-fix'
---
version: 2.0.0

# Linux 环境诊断与修复

> **动门先行，标源改制。** 环境故障本质是文件状态不一致，追踪到最晚写入的点即可根治。

## 1. MiKTeX "No space left" 假象

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
- **如果 .miktex 目录本身损坏**（如权限错误），可尝试 `rm -rf ~/.miktex/` 然后 `mpm --install=marticle` 重新初始化

## 2. Python 虚拟环境隔离

### 根因模式

**模式A：包装入了 uv 解释器自己的 site-packages，而非 venv 的 site-packages**

`uv pip install` 默认将包安装到**调用它的 Python 解释器的 site-packages**，而不是当前激活的 venv。如果 venv 配置了 `include-system-site-packages = false`，那么 venv 中的 Python 无法看到这些包。

**模式B：`~/.local/site-packages` 绕过 PEP 668**

`pip install --break-system-packages` 安装到 `~/.local/lib/python3.12/site-packages/`，这是系统 Python 的 site-packages，不受 venv 隔离保护。

**模式C：venv 的 python 是旧 symlink，指向的 Python 没有包**

`~/.venv/bin/python3` 可能 symlink 到一个 Python 二进制，但该二进制安装时没有包，实际包在另一个 Python 解释器中。

### 诊断步骤

```bash
# 1. 检查 venv 配置
cat ~/.venv/pyvenv.cfg

# 2. 检查 venv python 实际指向
ls -la ~/.venv/bin/python3
~/.venv/bin/python3 -c "import sys; print(sys.executable); print(sys.prefix); print(sys.path)"

# 3. 检查包安装位置
pip3 show <package> 2>/dev/null | grep Location
# 或
python3 -c "import <package>; print(<package>.__file__)"

# 4. 检查 PEP 668 状态
cat /usr/lib/python3.12/EXTERNALLY-MANAGED

# 5. 检查 ~/.local 中是否有系统级包
ls ~/.local/lib/python3.12/site-packages/ | wc -l
```

### 修复步骤

```bash
# 方案1：修改 venv 配置为 include-system-site-packages = true
# 然后确保 uv pip install 时通过正确的 python 路径安装
echo 'include-system-site-packages = true' > ~/.venv/pyvenv.cfg

# 方案2：使用 venv 自己的 pip 安装（如果存在）
~/.venv/bin/python3 -m pip install <package>

# 方案3：手动 symlink uv python 到 venv
ln -sf /home/yakeworld/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3 ~/.venv/bin/python3
ln -sf /home/yakeworld/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 ~/.venv/bin/python3.11
# 然后更新 pyvenv.cfg 使 include-system-site-packages = true
```

### 彻底清理系统 Python 污染（2026-06-21 新增）

当 `pip install --user` 将大量包污染到系统 Python 的 `~/.local/` 时，需要彻底清理：

```bash
# 1. 诊断污染范围
ls ~/.local/lib/python3.12/site-packages/ | wc -l  # 主版本
ls ~/.local/lib/python3.10/site-packages/ | wc -l  # 旧版本
ls ~/.local/lib/python3.8/site-packages/ | wc -l   # 更旧版本
ls ~/.local/bin/ | wc -l                            # pip 工具数

# 2. 修复 venv 隔离（关键第一步）
echo 'include-system-site-packages = false' > ~/.venv/pyvenv.cfg
# 确保 venv 不会看到系统 site-packages

# 3. 清理 ~/.local/lib/python3.X/site-packages
rm -rf ~/.local/lib/python3.12/site-packages/*
rm -rf ~/.local/lib/python3.10/site-packages/*
rm -rf ~/.local/lib/python3.8/site-packages/*

# 4. 清理 ~/.local/bin（所有 pip install --user 的工具）
rm -rf ~/.local/bin/*

# 5. 验证
ls ~/.local/lib/python3.12/site-packages/ | wc -l  # 应为 0
ls ~/.local/bin/ | wc -l                           # 应为 0
```

### Pitfall

- **`PIL` vs `Pillow`** — `import PIL` 成功但 `import Pillow` 失败。Python 模块名是 `PIL`，包名是 `Pillow`
- **`include-system-site-packages = true` 不会自动包含 uv 解释器的 site-packages** — 需要确认 venv 的 `sys.path` 中包含 uv python 的 site-packages 路径
- **不要直接删除 `~/.local/lib/python3.12/site-packages/` 而不先修复 venv** — 必须先设 `include-system-site-packages = false`，否则删除后 venv 依然能看到这些包（因为 venv 路径优先）
- **`~/.local/bin/` 不要随便删** — 里面可能有非 pip 工具。但如果是纯 pip 安装的工具（python script, ASCII text executable），可以安全删除
- **uv 的 pip 行为与 pip 不同** — `uv pip install` 不遵循 venv 隔离，直接安装到解释器的 site-packages
- **多 Python 版本共存** — `~/.local/lib/` 下可能有 python3.8, python3.10, python3.12 三个版本，每个都需要单独清理
- **uv Python 保留** — `~/.local/share/uv/python/` 下的 uv Python 解释器及其 site-packages 是 uv 管理的，不应删除

## 3. Playwright 浏览器安装

### 根因模式

**模式A：dpkg 中断导致 playwright install 失败**

```bash
# 错误信息
E: dpkg 被中断，您必须手工运行 'sudo dpkg --configure -a' 解决此问题。
```

**模式B：Chromium headless 在有 GUI Firefox 进程时 hang**

系统中运行的 Firefox GUI 进程（如 `snap/firefox`）可能与 Playwright headless 浏览器竞争资源。

### 诊断步骤

```bash
# 1. 检查已安装的浏览器
ls ~/.cache/ms-playwright/

# 2. 检查浏览器二进制
find ~/.cache/ms-playwright -name 'chrome*' -type f 2>/dev/null | head -5
find ~/.cache/ms-playwright -name 'firefox' -type f 2>/dev/null | head -3

# 3. 检查 dpkg 状态
sudo dpkg --configure -a 2>&1 | tail -5

# 4. 检查是否有残留 Firefox/Chromium 进程
ps aux | grep -i firefox | grep -v grep
ps aux | grep -i chrom | grep -v grep
```

### 修复步骤

```bash
# 1. 先修复 dpkg
sudo dpkg --configure -a

# 2. 安装 Playwright 浏览器（带系统依赖）
~/.venv/bin/python3 -m playwright install --with-deps chromium

# 3. 如果 chromium 有问题，试 firefox
~/.venv/bin/python3 -m playwright install --with-deps firefox

# 4. 验证
~/.venv/bin/python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('data:text/html,<h1>Hello</h1>')
    print(page.title())
    browser.close()
"
```

### Pitfall

- **`--with-deps` 需要 root 权限** — 安装浏览器依赖时需要 `sudo`。Playwright 内部会 switch to root
- **Chromium headless 在有 GUI Firefox 进程时可能 hang** — 如果测试 hang，尝试用 `firefox` 代替 `chromium`，或先杀掉 GUI Firefox 进程
- **Snap Firefox 和 Playwright Firefox 不冲突** — snap 版 Firefox 在 `/snap/firefox/`，Playwright Firefox 在 `~/.cache/ms-playwright/firefox-*/`，两者独立

## 4. 系统通用故障

### dpkg 中断

```bash
# 修复 dpkg 锁
sudo dpkg --configure -a
# 如果锁文件存在但进程已死
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

### 总结

环境故障诊断的核心原则：

1. **先查磁盘/inode** (`df -h`, `df -i`) — 很多时候不是真正的空间问题
2. **先查锁文件** — 损坏的锁是"假死"最常见原因
3. **先查 symlink** — `which` 返回的可能是 broken symlink
4. **先查路径** (`sys.path`, `PATH`) — 包在不在预期位置
5. **先查进程** (`ps aux`) — 残留进程可能导致资源竞争

## 参见

- `references/miktex-lock-troubleshooting.md` — MiKTeX 锁文件诊断的补充细节
- `references/python-venv-isolation-guide.md` — Python 虚拟环境隔离的完整指南
- `references/playwright-browser-setup.md` — Playwright 浏览器安装的完整流程

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
