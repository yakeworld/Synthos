# GNOME 桌面环境 IME 配置要点

## 背景

GNOME 桌面（Ubuntu 默认桌面环境）有自己的 IME 管理方式，与 `.bashrc` 中设置的环境变量并行。

## GNOME 的 IME 配置

### 通过 gnome-settings-daemon 管理
GNOME 的 settings-daemon 会覆盖或忽略部分 X11 IM 环境变量。IME 状态由 `gnome-control-center input` 或 `fcitx-config-gtk3` 管理。

### 确保 fcitx5 在 GNOME 中激活
```bash
# 检查 fcitx5 是否设为默认
gsettings get org.gnome.desktop.input-sources sources
# 期望输出: [('xkb', 'cn'), ('fcitx', '')] 或类似

# 如果为空或只有 xkb，添加 fcitx：
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'cn'), ('fcitx', '')]"
```

### GNOME 扩展
某些 GNOME 扩展（如 "Top Bar IM Status"）会管理 IM 状态栏显示。确保它们兼容 fcitx5。

## 与 .bashrc 环境变量的关系

`.bashrc` 中的 `GTK_IM_MODULE`、`QT_IM_MODULE`、`XMODIFIERS` 在以下场景生效：
1. **非 GNOME 会话**（如 startx、tty、tmux  detached session）— 完全依赖这些变量
2. **GNOME 内的终端模拟器**（gnome-terminal、tilix 等）— 这些应用会继承 shell 环境变量，同时 GNOME 也可能注入自己的值
3. **Hermes agent 的 `terminal()` 工具** — PTY 环境，无 GNOME 会话，完全依赖环境变量

**关键**：在 GNOME 桌面内运行 OpenCode 时，GTK 应用优先读取 GNOME 设置的 IM 配置。如果 GNOME 未正确配置 fcitx5，即使 `.bashrc` 正确，GTK 应用也可能不走 fcitx5。

## 诊断 GNOME IME 问题

```bash
# 1. 检查 GNOME input-sources 配置
gsettings get org.gnome.desktop.input-sources sources

# 2. 检查 gtk IM module 缓存
gtk-query-immodules-3.0 2>/dev/null | grep fcitx
gtk-query-immodules-4.0 2>/dev/null | grep fcitx

# 3. 验证 fcitx5 在 GNOME 中的状态
fcitx5-diagnose 2>/dev/null | head -50
```

## 参考

本参考文件补充了 `linux-ime` 主技能中 GNOME 桌面场景的配置要点。