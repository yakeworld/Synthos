# OpenCode 中文输入问题诊断

> **日期**：2026-06-14
> **状态**：根因已定位，修复方案已确认

## 根因

### 1. GTK_IM_MODULE 值错误
`~/.bashrc` 中设置了 `GTK_IM_MODULE=fcitx`（fcitx4 时代写法），但系统实际安装的是 fcitx5。

GTK3/4 应用（OpenCode 基于 Electron/Node，底层走 GTK4）需要 `GTK_IM_MODULE=fcitx5` 才能识别 fcitx5 的 IM module (`im-fcitx5.so`)。设置为 `fcitx` 时找不到对应模块。

### 2. PTY 模式下 fcitx5 无法工作
Hermes `terminal(pty=true)` 创建纯虚拟终端，无 X11 会话。fcitx5 daemon 连接的是 X11 display `:1`，PTY 子进程不共享 XIM 连接，fcitx5 无法注入中文到非图形终端。

## 修复方案

### 桌面环境（手动运行 opencode）
```bash
# 修改 ~/.bashrc
GTK_IM_MODULE=fcitx5   # 替换 fcitx → fcitx5
```
然后 `source ~/.bashrc` 并重开终端。

### Hermes agent 通过 terminal() 工具
PTY 内 fcitx5 不可用。替代方案：
- 直接在 `terminal()` 的 text 参数传中文文本（不经过 PTY IM）
- 用 `write_file()` 写入中文内容

## 验证
```bash
GTK_IM_MODULE=fcitx5 QT_IM_MODULE=fcitx5 XMODIFIER=@im=fcitx5 \
  opencode --version  # 正常启动
```

## 相关文件
- GTK IM modules: `/usr/lib/x86_64-linux-gnu/gtk-3.0/3.0.0/immodules/im-fcitx5.so`
- GTK IM modules: `/usr/lib/x86_64-linux-gnu/gtk-4.0/4.0.0/immodules/libim-fcitx5.so`
- fcitx5 daemon: PID 65417, 监听 `/run/user/1000/fcitx` socket
