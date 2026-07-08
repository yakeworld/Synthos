# Hermes Agent — Windows 分发方案

> 目标：Windows 用户"拷即用"——下载、双击、运行，无需任何预装。

---

## 最终方案：PowerShell 一键安装 + 便携包

### 用户路径

```
1. 下载 hermes-windows.zip (20MB)
   ├── hermes-windows-setup.ps1    # 一键安装脚本（5分钟）
   ├── hermes-gui.py               # 交互式启动器
   ├── run-hermes.bat              # 命令行快捷方式
   ├── README.md                   # 一页纸说明

2. 解压 → 双击 .ps1 → 等5分钟

3. 安装完成，桌面有快捷方式

4. 双击快捷方式 → 使用
   或: python hermes-gui.py → 输入问题 → 获取回答
```

### 文件清单

| 文件 | 用途 | 大小 |
|------|------|------|
| `hermes-windows-setup.ps1` | 一键安装脚本（Python + uv + Hermes + Node + OpenCode + 配置） | 8KB |
| `hermes-gui.py` | 交互式 Python 启动器（纯文本输入/输出） | 2KB |
| `run-hermes.bat` | 命令行快捷启动 | 0.5KB |
| `README.md` | 使用说明 | 2KB |

总下载量：~20MB（脚本很小，但会下载 Python 3.12 + Node.js 运行时）

---

## 安装脚本流程 (`hermes-windows-setup.ps1`)

```
Step 1: Python
  - 检测系统是否有 Python 3.12+
  - 没有 → 自动下载安装（python.org）
  - 有 → 跳过

Step 2: uv
  - 通过 pip 安装 uv
  - 比 pip 快10倍

Step 3: Hermes Agent
  - 通过 pipx 安装
  - 确保 PATH 配置

Step 4: Node.js + OpenCode
  - 检测系统是否有 Node.js
  - 没有 → 自动下载安装（nodejs.org）
  - npm install -g @ai-sdk/opencode

Step 5: 配置文件
  - 创建 ~/.hermes/config.yaml（模板）
  - 创建 ~/.config/opencode/opencode.json

Step 6: 快捷方式
  - 创建桌面快捷方式 "Hermes Agent"
  - 创建 run-hermes.bat（命令行快捷方式）
  - 创建 run-opencode.bat

Step 7: 验证
  - 检查所有组件是否安装成功
  - 输出验证报告
```

---

## 使用方式

### 方式1：GUI 交互式（推荐新手）

```
cd hermes-windows
python hermes-gui.py
>> 帮我写一段 Python 计算瞳孔椭圆3D法向量
```

### 方式2：命令行

```
hermes chat -q "你的问题" -Q
```

### 方式3：桌面快捷方式

双击桌面的 "Hermes Agent" 图标。

### 方式4：OpenCode

```
opencode -m hermes/qwen3.6-35b-nvfp4
```

---

## 更新

用户只需重新运行安装脚本即可：

```powershell
powershell -ExecutionPolicy Bypass -File hermes-windows-setup.ps1
```

脚本会检测已有安装，跳过已安装的步骤。

---

## 已知限制

1. **需要网络连接** — 首次安装需要从 python.org 和 nodejs.org 下载
2. **需要管理员权限** — 安装 Python/Node 时需要写 Program Files
3. **PowerShell 5.1+** — Win10/11 自带，Win7 不支持
4. **x64 架构** — 目前只支持 Windows 64 位

---

## 未来改进方向

1. **PyInstaller 打包** — 把 Hermes 打包成独立 EXE，完全不需要系统 Python
2. **内嵌 Node.js** — 把 Node.js 二进制内嵌到包中，不需要下载安装
3. **自动更新** — 启动时检查版本，自动下载更新
4. **图形界面** — 用 PyQt/Tkinter 做真正的 GUI，而非终端输入
5. **离线模式** — 预装常用技能和模板，无需联网

---

## 打包脚本（服务器端）

```bash
# 创建发布包
cd /path/to/Synthos/docker
zip -r ../hermes-windows.zip \
    hermes-windows-setup.ps1 \
    hermes-gui.py \
    run-hermes.bat \
    README-Windows.md

# 上传到 GitHub Releases 或下载站点
```

---

## 分发渠道

1. **GitHub Releases** — 版本化发布，自动更新通知
2. **Synthos 仓库 wiki** — 下载页
3. **X/Twitter** — 推广帖 + 下载链接
4. **小红书** — 中文教程帖 + 下载链接