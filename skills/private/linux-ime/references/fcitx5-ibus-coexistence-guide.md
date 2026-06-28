# fcitx5 ↔ ibus 切换指南

> 记录 fcitx5 与 ibus 输入法框架切换时的完整流程，避免配置残留。

## 切换原则

**每次切换输入法框架，必须执行三步清理**：
1. 停止旧框架 daemon
2. 删除旧框架的 xinput.d 配置文件
3. 更新环境变量（environment.d + .bashrc）

## 从 fcitx5 切换到 ibus

### 第1步：停止 fcitx5
```bash
killall fcitx5 2>/dev/null
```

### 第2步：删除 fcitx5 的 xinput 配置
```bash
sudo rm /etc/X11/xinit/xinput.d/fcitx
```

### 第3步：创建 ibus 的 xinput 配置
```bash
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

### 第4步：更新环境变量
```bash
# 更新 /etc/environment.d/ibus.conf
cat > /etc/environment.d/ibus.conf << 'EOF'
GTK_IM_MODULE=ibus
QT_IM_MODULE=ibus
XMODIFIERS=@im=ibus
EOF

# 更新 ~/.bashrc
sed -i 's/^GTK_IM_MODULE=fcitx5$/GTK_IM_MODULE=ibus/' ~/.bashrc
sed -i 's/^QT_IM_MODULE=fcitx5$/QT_IM_MODULE=ibus/' ~/.bashrc
sed -i 's/^XMODIFIERS=@im=fcitx5$/XMODIFIERS=@im=ibus/' ~/.bashrc
```

### 第5步：启动 ibus-daemon
```bash
ibus-daemon -dr 2>&1
# 确认子进程都在运行
pgrep -a ibus-daemon
pgrep -a ibus-dconf
pgrep -a ibus-ui-gtk3
```

### 第6步：注销再登录
```bash
# 或重启 GDM
sudo systemctl restart gdm3
```

## 从 ibus 切换到 fcitx5

### 第1步：停止 ibus-daemon
```bash
killall ibus-daemon 2>/dev/null
```

### 第2步：删除 ibus 的 xinput 配置
```bash
sudo rm /etc/X11/xinit/xinput.d/ibus 2>/dev/null
```

### 第3步：创建 fcitx5 的 xinput 配置
```bash
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

### 第4步：更新环境变量
```bash
# 删除或覆盖 /etc/environment.d/ibus.conf
rm /etc/environment.d/ibus.conf

cat > /etc/environment.d/fcitx.conf << 'EOF'
GTK_IM_MODULE=fcitx5
QT_IM_MODULE=fcitx5
XMODIFIERS=@im=fcitx5
EOF

# 更新 ~/.bashrc
sed -i 's/^GTK_IM_MODULE=ibus$/GTK_IM_MODULE=fcitx5/' ~/.bashrc
sed -i 's/^QT_IM_MODULE=ibus$/QT_IM_MODULE=fcitx5/' ~/.bashrc
sed -i 's/^XMODIFIERS=@im=ibus$/XMODIFIERS=@im=fcitx5/' ~/.bashrc
```

### 第5步：启动 fcitx5
```bash
fcitx5 --replace -d 2>&1
```

### 第6步：注销再登录
```bash
sudo systemctl restart gdm3
```

## 验证清单

切换完成后，逐项检查：

```bash
# 1. 环境变量正确
env | grep -i "GTK_IM_MODULE"
# 期望值应为当前框架

# 2. 无旧框架 xinput.d 残留
cat /etc/X11/xinit/xinput.d/fcitx 2>/dev/null && echo "警告：fcitx 残留"
cat /etc/X11/xinit/xinput.d/ibus 2>/dev/null && echo "警告：ibus 残留"

# 3. 当前框架 daemon 运行
pgrep -a fcitx5  # 或 ibus-daemon

# 4. 子进程完整性（ibus）
pgrep -a ibus-dconf && pgrep -a ibus-ui-gtk3

# 5. GNOME 输入源设置
gsettings get org.gnome.desktop.input-sources sources

# 6. IM module 文件存在
ls /usr/lib/x86_64-linux-gnu/gtk-3.0/*/immodules/ | grep -E "(fcitx5|ibus)"
```

## 常见故障

| 症状 | 原因 | 修复 |
|------|------|------|
| Chrome/Firefox 无法输入中文 | 浏览器未重启 | 完全关闭浏览器再打开 |
| 候选窗口不出现 | xinput.d 残留旧配置 | 删除残留，创建新配置，注销登录 |
| GNOME 设置中无中文输入源 | GNOME 输入源未更新 | `gsettings set org.gnome.desktop.input-sources "[(('xkb', 'us'), ('ibus', 'pinyin'))]"` |
| ibus-daemon 启动但无子进程 | ibus-dconf/ibus-ui-gtk3 未启动 | 重新运行 `ibus-daemon -dr` |
| Firefox snap 版不识别 GTK_IM_MODULE | snap 沙箱隔离 | 安装 deb 版 Firefox |
