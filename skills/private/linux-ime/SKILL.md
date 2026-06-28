---
name: linux-ime
description: Linux 输入法（IME）诊断与修复 — fcitx/fcitx5 配置不匹配、GTK_IM_MODULE/QT_IM_MODULE/XMODIFIERS 三环境变量修复、X11/Wayland 差异、pty 环境 IME 不可用的根因分析与修复。
metadata:
  synthos:
    priority: P2
    atom_type: class-level
    description: "Linux 输入法（IME）诊断与修复 — 覆盖 fcitx/fcitx5 配置检查、GTK_IM_MODULE/QT_IM_MODULE/XMODIFIERS 三环境变量修复、X11/Wayland 差异、pty 环境限制。"
signature: "linux-ime -> processed_result"
---
version: 1.0.0

# Linux IME 诊断与修复

> **文以验法，技乃所产。** 输入法失效是配置漂移的表象，追查至变量源头即可根治。

## 根因模式

### 模式1：GTK_IM_MODULE 值错误（最常见）
- 系统安装了 fcitx5，但 `.bashrc`/`/etc/environment` 中设置的是 `GTK_IM_MODULE=fcitx`（fcitx4 时代的值）
- GTK3/4 应用启动时找不到 `im-fcitx.so`（不存在），只能 `im-fcitx5.so`
- **表现**：应用能运行，但中文候选窗口不出现，或中文无法输入

### 模式2：XMODIFIERS 错配
- `XMODIFIERS=@im=fcitx` 指向 fcitx4，实际运行的是 fcitx5
- Qt 应用和某些 GTK 应用依赖此变量建立 XIM 连接

### 模式3：fcitx4 与 fcitx5 混装
- dpkg 状态同时存在 `rc`（已 purge）的 fcitx4 包和 `ii` 的 fcitx5 包
- `/etc/X11/xinit/xinput.d/` 下只有 fcitx 文件（指向 fcitx4）
- 配置文件残留导致新安装的应用仍读取旧配置

### 模式4：Snap 版 Firefox 硬编码 ibus（常见陷阱）
- Ubuntu 默认安装 snap 版 Firefox，编译时硬编码使用 ibus 后端
- **不受 `GTK_IM_MODULE` 环境变量影响**——Firefox 内部直接连接 ibus DBus 总线
- **AppArmor 沙箱隔离**：snap 容器内的 Firefox 无法连接系统 ibus-daemon
- **表现**：即使环境变量设为 `fcitx5`，Firefox 仍报 `IBUS-CRITICAL: ibus_bus_is_connected == FALSE` 错误
- **解决**：
  1. `sudo snap remove firefox` → `sudo apt install firefox`（安装 deb 版）
  2. `sudo apt-mark hold firefox` 防止 snap 自动重装
  3. 或者在 `about:config` 中设置 `toolkit.ime.use_xim=false`
- **诊断要点**：`which firefox` 在 Ubuntu 上常返回 `/usr/bin/firefox`，但这是**shell 脚本**（transitional package），不是二进制文件。用 `file $(which firefox)` 检测——脚本是 POSIX shell script，bin 才是 ELF。脚本内容会检查 `/snap/bin/firefox` 是否存在，存在则 `exec` 到 snap 版。

### 模式4b：Chromium 同名 snap 陷阱
- `chromium-browser` 包在 Ubuntu 24.04+ 是 transitional，实际走 `chromium snap`
- 路径 `readlink -f /usr/bin/chromium-browser` → `/snap/bin/chromium`
- 同样硬编码 ibus，不受 GTK_IM_MODULE 影响
- 诊断：`snap list chromium` 和 `dpkg -l | grep chromium | grep transitional`

### 模式5：fcitx5 ↔ ibus 切换时 xinput.d 残留配置
- 当用户从 fcitx5 切换回 ibus（或反之）时，**必须删除旧版本的 xinput 配置文件**
- 例如 fcitx5 的 `/etc/X11/xinit/xinput.d/fcitx` 中包含 `GTK_IM_MODULE=fcitx5`，会覆盖 ibus 的配置
- **诊断**：执行 `cat /etc/X11/xinit/xinput.d/fcitx` 检查是否有 fcitx4/5 残留
- **修复**：删除旧配置，创建对应版本的配置文件（见"修复命令"部分）
- **注意**：切换输入法框架后必须注销再登录（或重启 GDM）才能生效

### 模式6：GNOME 46+ native IM 支持变化
- GNOME 46 移除了独立的 ibus GNOME shell applet，改用原生 IM 支持
- ibus 不再需要额外的 `gnome-shell-extension-ibus` 包
- 如果 ibus-daemon 启动但候选窗口不出现，检查 `ibus-dconf` 和 `ibus-ui-gtk3` 是否都在运行
- 检查 GNOME Shell 的 `enabled-extensions` 是否仍有旧版 ibus 扩展残留

### 模式7：pty/Tmux 环境中 IME 不可用
- Hermes `terminal(pty=true)` 创建的是纯虚拟终端
- 无 X11 display 或 Wayland socket，fcitx5/ibus daemon 无法注入候选
- **解决**：在 GUI 终端中直接输入，或通过 `write_file()` 写入中文内容

### 模式8：ibus-libpinyin 性能问题（云候选延迟）
- `ibus-libpinyin` 的网络候选 + 云端词频预测（opengram）是输入法延迟的主要来源
- **诊断**：`ls ~/.config/ibus/libpinyin/` — 关注 `network.bin`、`opengram.dbin`、`user.conf`
- **修复**：参考 `references/ibus-libpinyin-performance-tuning.md`
  1. 禁用网络候选：`echo "enableNetworkCandidate=false" >> ~/.config/ibus/libpinyin/user.conf`
  2. 移除网络数据：`rm -f ~/.config/ibus/libpinyin/network.bin ~/.config/ibus/libpinyin/opengram.dbin`
  3. 显式声明 GTK IM：`~/.config/gtk-{3,4}.0/gtk.conf` 写入 `gtk-im-module=ibus`
  4. 重启 ibus-daemon：`kill $(pgrep ibus-daemon) && ibus-daemon -d -x`

## 诊断步骤（按顺序执行）

1. **确认 fcitx 版本**
   ```bash
   dpkg -l | grep fcitx | grep "^ii"  # 查看已安装的 fcitx 版本
   pgrep -a fcitx5                     # 查看运行中的进程
   ```

2. **检查环境变量**
   ```bash
   env | grep -i "GTK_IM\|QT_IM\|XMODIFIERS"
   ```
   期望值：
   - `GTK_IM_MODULE=fcitx5`（或 ibus，取决于使用的框架）
   - `QT_IM_MODULE=fcitx5`（或 ibus）
   - `XMODIFIERS=@im=fcitx5`（或 @im=ibus）

3. **检查环境文件优先级（关键！）**
   - `/etc/environment.d/*.conf` — **最高优先级**，PAM 登录会话时加载，覆盖所有用户配置
   - `/etc/X11/xinit/xinput.d/fcitx` — **X11 会话启动时读取，会覆盖 /etc/environment.d 中的设置！** 这是最常见的覆盖陷阱
   - `~/.bashrc` / `~/.profile` — 仅影响新终端会话，对 GUI 应用可能不生效
   ```bash
   cat /etc/environment.d/fcitx.conf 2>/dev/null  # 常见陷阱：fcitx4 遗留
   cat /etc/X11/xinit/xinput.d/fcitx 2>/dev/null  # 常见陷阱：fcitx4 遗留，覆盖 environment.d
   grep -n "GTK_IM\|QT_IM\|XMODIFIERS" ~/.bashrc ~/.profile ~/.pam_environment 2>/dev/null
   ```
   **注意**：`/etc/X11/xinit/xinput.d/fcitx` 中的 `GTK_IM_MODULE` 值会覆盖 `/etc/environment.d/` 中的设置。检查顺序：xinput.d > environment.d > .bashrc

4. **检查 GNOME 输入源设置**
   ```bash
   gsettings get org.gnome.desktop.input-sources sources
   ```
   期望值应包含 `fcitx` 或 `ibus`（取决于使用的框架），而非两者冲突。

5. **验证 IM module 文件存在**
   ```bash
   ls /usr/lib/x86_64-linux-gnu/gtk-3.0/*/immodules/*fcitx* 2>/dev/null
   ls /usr/lib/x86_64-linux-gnu/gtk-4.0/*/immodules/*fcitx* 2>/dev/null
   # 或对于 ibus：
   ls /usr/lib/x86_64-linux-gnu/gtk-3.0/*/immodules/im-ibus.so 2>/dev/null
   ```

6. **检查 Firefox 是否为 snap 版**
   ```bash
   which firefox && snap list firefox 2>/dev/null
   readlink -f $(which firefox)  # snap 版路径含 /snap/firefox/
   ```
   如果是 snap 版，环境变量不生效，必须安装 deb 版。

7. **检查输入法框架进程完整性**
   ```bash
   # 对于 ibus：
   pgrep -a ibus-daemon
   pgrep -a ibus-dconf
   pgrep -a ibus-ui-gtk3
   # 对于 fcitx5：
   pgrep -a fcitx5
   ```
   缺少子进程会导致候选窗口不出现。

## 修复命令

### 修复 .bashrc（用户级，立即生效需重启终端）
```bash
# 统一改为 fcitx5
sed -i 's/^GTK_IM_MODULE=fcitx$/GTK_IM_MODULE=fcitx5/' ~/.bashrc
sed -i 's/^QT_IM_MODULE=fcitx$/QT_IM_MODULE=fcitx5/' ~/.bashrc
sed -i 's/^XMODIFIERS=@im=fcitx$/XMODIFIERS=@im=fcitx5/' ~/.bashrc
```

### 当前会话立即生效（不重启）
```bash
export GTK_IM_MODULE=fcitx5
export QT_IM_MODULE=fcitx5
export XMODIFIERS=@im=fcitx5
```

### 修复 fcitx5 xinput 配置（需要 root 权限）
```bash
# 删除旧配置
sudo rm /etc/X11/xinit/xinput.d/fcitx
# 创建 fcitx5 版本
sudo tee /etc/X11/xinit/xinput.d/fcitx5 > /dev/null << 'EOF'
XIM=fcitx5
XIM_PROGRAM=/usr/bin/fcitx5
XIM_ARGS="--daemon-started"
GTK_IM_MODULE=fcitx5
QT_IM_MODULE=fcitx5
XCINIF=xim
DEPENDS="fcitx5"
EOF
```

### 修复 ibus xinput 配置（需要 root 权限）
```bash
# 删除旧配置（如 fcitx5 残留）
sudo rm /etc/X11/xinit/xinput.d/fcitx
# 创建 ibus 版本
sudo tee /etc/X11/xinit/xinput.d/ibus > /dev/null << 'EOF'
XIM=ibus
XIM_PROGRAM=/usr/bin/ibus-daemon
XIM_ARGS="--daemon"
GTK_IM_MODULE=ibus
QT_IM_MODULE=ibus
XCINIF=xim
DEPENDS="ibus"
EOF
```

## 验证

```bash
# 环境变量正确
env | grep -i "GTK_IM_MODULE=fcitx5\|GTK_IM_MODULE=ibus"

# fcitx5 daemon 运行
pgrep -a fcitx5
# 或 ibus daemon 运行
pgrep -a ibus-daemon

# IM module 文件存在
ls -la /usr/lib/x86_64-linux-gnu/gtk-3.0/*/immodules/im-fcitx5.so
ls -la /usr/lib/x86_64-linux-gnu/gtk-3.0/*/immodules/im-ibus.so

# 检查 xinput.d 中无旧配置残留
cat /etc/X11/xinit/xinput.d/fcitx 2>/dev/null && echo "警告：仍有 fcitx 残留配置！"

# 应用重启后测试中文输入
```

## Pitfalls

- **环境变量注入后应用不生效**：GTK/Qt 应用在启动时读取 IM 模块，已在运行中的进程需要完全关闭再重启
- **fcitx4 残留配置干扰**：检查 `/etc/X11/xinit/xinput.d/fcitx`（fcitx4 文件）是否仍然存在，如有应创建对应的 fcitx5 版本并确认应用读取的是 fcitx5 版本
- **Snap Firefox 不识别 GTK_IM_MODULE**：snap 版 Firefox 硬编码使用 ibus，必须安装 deb 版。先查 `which firefox && snap list firefox`，路径含 `/snap/firefox/` 即为 snap 版
- **/etc/environment.d/fcitx.conf 优先级最高**：PAM 登录会话时加载，覆盖 `.bashrc`。很多会话里 `.bashrc` 已设为 fcitx5 但 `/etc/environment.d/fcitx.conf` 还是 `fcitx`（fcitx4 值），导致 GUI 应用被覆盖
- **pty 环境中 fcitx5 不工作**：虚拟终端无 X11 会话，fcitx5 daemon 无法注入。这是设计限制，不是 bug
- **多版本混装时优先使用 fcitx5**：系统可同时安装 fcitx4（残留）和 fcitx5，所有配置应统一指向 fcitx5
- **fcitx5 ↔ ibus 切换时 `/etc/X11/xinit/xinput.d/` 残留配置**：当用户从 fcitx5 切换回 ibus（或反之）时，必须删除旧版本的 xinput 配置文件。例如 fcitx5 的 `/etc/X11/xinit/xinput.d/fcitx` 中包含 `GTK_IM_MODULE=fcitx5`，会覆盖 ibus 的配置。诊断：执行 `cat /etc/X11/xinit/xinput.d/fcitx` 检查是否有 fcitx4/5 残留，如有应删除或覆盖为对应版本的配置。切换输入法框架后必须注销再登录（或重启 GDM）才能生效。
- **GNOME 46+ native IM 支持变化**：GNOME 46 移除了独立的 ibus GNOME shell applet，改用原生 IM 支持。检查 `ibus-dconf` 和 `ibus-ui-gtk3` 子进程是否都在运行。

## 参见

- `references/gnome-desktop-ime-setup.md` — GNOME 桌面环境 IME 配置要点
- `references/fcitx5-ibus-coexistence-guide.md` — fcitx5 与 ibus 共存/切换指南，包含 xinput.d 残留处理流程
- `references/ibus-libpinyin-performance-tuning.md` — ibus-libpinyin 性能优化：禁用云候选、词频预测、显式 GTK 配置

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。
