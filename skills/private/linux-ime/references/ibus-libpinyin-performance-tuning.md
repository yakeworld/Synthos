# ibus-libpinyin 性能优化指南

> 用户环境 Ubuntu 24.04.4 LTS，GNOME X11 会话，ibus-libpinyin 中文输入延迟高。
> 通过禁用云候选、清空词频预测缓存、显式 GTK 配置实现性能提升。

## 诊断慢输入

```bash
# 确认使用 ibus-libpinyin
dpkg -l | grep ibus | grep engine
# 确认 libpinyin 数据目录
ls ~/.config/ibus/libpinyin/
# 关键文件：network.bin（网络候选）、opengram.dbin（云端词频预测）、user.conf
```

## 优化步骤（按收益排序）

### 第1步：禁用网络候选（最大收益）

网络候选请求是延迟的主要来源。移除网络数据文件 + 写入配置：

```bash
# 备份
cp ~/.config/ibus/libpinyin/network.bin ~/.config/ibus/libpinyin/network.bin.bak
cp ~/.config/ibus/libpinyin/opengram.dbin ~/.config/ibus/libpinyin/opengram.dbin.bak

# 禁用云候选
mkdir -p ~/.config/ibus/libpinyin
echo "enableNetworkCandidate=false" >> ~/.config/ibus/libpinyin/user.conf

# 移除网络数据文件
rm -f ~/.config/ibus/libpinyin/network.bin
rm -f ~/.config/ibus/libpinyin/opengram.dbin
```

### 第2步：显式声明 GTK IM 模块（减少探测延迟）

GTK 应用在启动时会探测可用的 IM 模块，显式声明可跳过探测：

```bash
mkdir -p ~/.config/gtk-3.0 ~/.config/gtk-4.0
echo "[Settings]" > ~/.config/gtk-3.0/gtk.conf
echo "gtk-im-module=ibus" >> ~/.config/gtk-3.0/gtk.conf
echo "[Settings]" > ~/.config/gtk-4.0/gtk.conf
echo "gtk-im-module=ibus" >> ~/.config/gtk-4.0/gtk.conf
```

### 第3步：重启 ibus-daemon

```bash
# 杀掉旧进程
kill $(pgrep ibus-daemon) 2>/dev/null
# 干净重启
ibus-daemon -d -x 2>&1
# 确认子进程
pgrep -a ibus-daemon
pgrep -a ibus-dconf
pgrep -a ibus-ui-gtk3
```

## 效果验证

- 打字无网络延迟感（候选框即时弹出）
- 浏览器（含 snap 版 Firefox/Chromium）输入正常
- GTK/Qt 应用输入流畅

## Pitfalls

- **只重启终端不够**：ibus-daemon 需要完全重启才能生效，GTK/Qt 应用也需要完全关闭再打开
- **opengram.dbin 会被重建**：ibus-libpinyin 重新运行时会从用户词库重建词频，不影响已生效的 `enableNetworkCandidate=false`
- **如果后续想恢复网络候选**：从 `.bak` 文件恢复 `network.bin` 和 `opengram.dbin`，删除 `enableNetworkCandidate=false`，重启 ibus-daemon