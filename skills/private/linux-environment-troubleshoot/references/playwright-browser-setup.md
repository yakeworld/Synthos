# Playwright 浏览器安装指南

## 浏览器安装路径

```
~/.cache/ms-playwright/
├── chromium-1223/
│   ├── chrome-linux64/
│   │   ├── chrome           # 主二进制
│   │   ├── chrome-wrapper   # wrapper 脚本
│   │   ├── chrome_crashpad_handler
│   │   ├── chrome_sandbox
│   │   └── ...
│   └── ...
├── chromium_headless_shell-1217/
├── chromium_headless_shell-1223/
├── firefox-1522/
│   └── firefox/
│       └── firefox          # 主二进制
├── webkit-2287/
└── ffmpeg-1011/
```

## 安装步骤

### 1. 修复 dpkg 状态（必须先执行）
```bash
sudo dpkg --configure -a
```
如果报错 `E: dpkg 被中断，您必须手工运行 'sudo dpkg --configure -a'`，必须先执行此命令。

### 2. 安装 Playwright 浏览器
```bash
# 安装 chromium + 系统依赖
python3 -m playwright install --with-deps chromium

# 或 firefox
python3 -m playwright install --with-deps firefox

# 或 webkit
python3 -m playwright install --with-deps webkit
```

`--with-deps` 会自动安装系统依赖（libnss3, libatk1.0-0, 等），需要 root 权限。

### 3. 验证安装
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 测试 chromium
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('data:text/html,<h1>Hello World</h1>')
    print('Chromium OK:', page.title())
    browser.close()
    
    # 测试 firefox
    browser = p.firefox.launch(headless=True)
    page = browser.new_page()
    page.goto('data:text/html,<h1>Hello World</h1>')
    print('Firefox OK:', page.title())
    browser.close()
```

## 常见问题

### Chromium headless hang

**症状**：`p.chromium.launch()` 后无响应，进程挂起。

**原因**：系统中运行的 GUI Firefox 进程（`snap/firefox`）可能与 Playwright headless 浏览器竞争资源。GUI Firefox 进程数可达 26+ 个子进程。

**排查**：
```bash
ps aux | grep -i firefox | grep -v grep  # 检查残留 Firefox 进程
ps aux | grep -i chrom | grep -v grep     # 检查残留 Chromium 进程
```

**解决**：
1. 尝试使用 `firefox` 代替 `chromium`：`p.firefox.launch(headless=True)`
2. 如果仍然 hang，尝试 `headless_shell` 代替完整 Chrome
3. 杀掉残留的 GUI 进程：`pkill -f firefox` 或 `pkill -f chromium`

### Firefox snap 与 Playwright Firefox 冲突

**不冲突**：Snap Firefox 在 `/snap/firefox/`，Playwright Firefox 在 `~/.cache/ms-playwright/firefox-*/`，两者独立。

### dpkg 中断

**症状**：`playwright install` 时报 `E: dpkg 被中断`。

**原因**：之前有 `apt` 操作被中断（Ctrl+C、SSH 断开等），dpkg 锁未释放。

**解决**：
```bash
sudo dpkg --configure -a
# 如果仍然失败：
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

## 验证清单

```bash
# 1. 浏览器目录存在
ls -la ~/.cache/ms-playwright/chromium-1223/
ls -la ~/.cache/ms-playwright/firefox-1522/

# 2. 浏览器二进制存在
find ~/.cache/ms-playwright -name 'chrome*' -type f 2>/dev/null | head -5
find ~/.cache/ms-playwright -name 'firefox' -type f 2>/dev/null | head -3

# 3. playwright Python 包版本
python3 -c "import importlib.metadata; print(importlib.metadata.version('playwright'))"

# 4. 浏览器驱动版本
python3 -c "
import subprocess
result = subprocess.run(['python3', '-m', 'playwright', 'install', '--dry-run', 'chromium'],
                       capture_output=True, text=True)
print(result.stdout[:200])
"
```
