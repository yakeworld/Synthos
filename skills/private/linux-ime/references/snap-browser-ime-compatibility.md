# Snap 浏览器输入法兼容性陷阱

## 问题本质

Ubuntu 默认通过 snap 安装 Firefox 和 Chromium，它们的编译后端是硬编码的：

| 浏览器 | 硬编码后端 | 原因 |
|--------|-----------|------|
| Firefox (snap) | ibus | Mozilla 编译时绑定 ibus |
| Chromium (snap) | ibus | Ubuntu snap 包绑定 ibus |

Snap 容器使用 AppArmor 沙箱隔离，**容器内的浏览器无法连接宿主机上的 fcitx5 daemon**。

## 诊断

### 标准诊断
```bash
# 检查是否为 snap 版
readlink -f $(which firefox chromium-browser google-chrome)
# snap 版输出含 /snap/firefox/ 或 /snap/chromium/
snap list firefox chromium-browser
```

### Ubuntu transitional package 陷阱（2026-06-20 新增）
Ubuntu 24.04+ 的 `firefox` 和 `chromium-browser` 包是 transitional shell 脚本，不是二进制文件：

```bash
# 检测方法1：file 命令
file $(which firefox)
# shell 脚本输出: POSIX shell script, ASCII text executable
# 二进制输出: ELF 64-bit LSB pie executable

# 检测方法2：读文件头
head -3 /usr/bin/firefox
# snap 版 transitional 脚本首行为: #!/bin/sh
# deb 版二进制: (binary content)

# 检测方法3：snap list
snap list firefox chromium
# 有输出 = snap 版仍在

# 检测方法4：dpkg 包名
dpkg -l | grep firefox | grep transitional
# 有输出 = transitional package，实际走 snap
```

Ubuntu 的 `/usr/bin/firefox` transitional 脚本内容：
```sh
#!/bin/sh
if ! [ -x /snap/bin/firefox ]; then
    echo "Command '$0' requires the firefox snap to be installed." >&2
    exit 1
fi
exec /snap/bin/firefox "$@"
```
这个脚本检查 `/snap/bin/firefox` 存在才执行。移除 snap 后脚本失效，需要安装 deb 版并替换。

## 影响范围

- **fcitx5 用户**：Chrome/Firefox 无法使用中文输入，其他 GTK/Qt 应用正常
- **ibus 用户**：无影响，Snap 浏览器原生支持 ibus

## 解决方案

### 方案1：使用 ibus（推荐，浏览器原生兼容）
Ubuntu 默认即 ibus，无需额外配置，所有浏览器（含 snap）正常工作。
优化 ibus-libpinyin 延迟：
- 删除 `~/.config/ibus/libpinyin/network.bin` 和 `opengram.dbin`
- `enableNetworkCandidate=false` 写入 `~/.config/ibus/libpinyin/user.conf`
- 显式声明 GTK IM 模块：`~/.config/gtk-3.0/gtk.conf` 和 `~/.config/gtk-4.0/gtk.conf`
- 重启 `ibus-daemon -rd`

### 方案2：安装 deb 版浏览器
```bash
# 移除 snap 版
sudo snap revert firefox  # 先 revert 避免 "active revision" 错误
sudo snap remove firefox

# 添加 Mozilla PPA
sudo add-apt-repository -y ppa:mozillateam/ppa
sudo apt update

# 设置 apt 优先级阻止 snap 重装
sudo tee /etc/apt/preferences.d/firefox > /dev/null << 'EOF'
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
EOF

# 安装 deb 版
sudo apt install -y --reinstall --allow-downgrades firefox

# 防止 snap 自动重装
sudo apt-mark hold firefox chromium-browser
```

### 方案3：Firefox 专用 hack
在 `about:config` 中设置 `toolkit.ime.use_xim = false`，强制使用不同 IM 路径。

## Chromium snap 移除注意事项
Chromium snap 较大（~191MB），`snap remove chromium` 可能卡住（文件清理慢）。
- 可用 `snap changes` 查看移除进度
- 卡住时 `snap abort <change_id>` 可强制中止
- 注意：强制操作可能有数据风险，谨慎使用

## 证据

- 2026-06-20 会话：用户 fcitx5 配置完整但 Chrome/Firefox 无法输入中文。
- 诊断发现 Firefox 和 Chromium 均为 snap 版，通过 transitional shell 脚本调用。
- snap Firefox 版本 152.0.1-1 (revision 8521)。
- Ubuntu 24.04 默认 snap Firefox/Chromium 版本均不受 GTK_IM_MODULE 影响。
