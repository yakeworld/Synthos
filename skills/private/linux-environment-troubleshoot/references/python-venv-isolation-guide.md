# Python 虚拟环境隔离指南

## uv 管理的 venv 结构

Ubuntu 24.04 上 uv 安装的 Python 位于：
```
~/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3
```

对应的 venv（`pyvenv.cfg`）：
```
home = /home/yakeworld/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.11
version_info = 3.11.15
include-system-site-packages = true  # 关键：需要设为 true 才能访问 uv python 的包
prompt = yakeworld
```

## 关键行为

### uv pip install 的行为
- `uv pip install <pkg>` 安装到**当前 Python 解释器**的 site-packages
- 如果通过 `~/.venv/bin/python3 -m pip install` 安装，安装到 `~/.venv/bin/python3` 对应的解释器的 site-packages
- 如果 venv 配置了 `include-system-site-packages = false`，venv 不会看到系统包

### Python 路径继承
当 `include-system-site-packages = true` 时，venv 的 `sys.path` 包含：
```
/home/yakeworld/.venv/lib/python3.11/site-packages     # venv 自己的 site-packages（优先）
/home/yakeworld/.local/share/uv/python/cpython-3.11.../lib/python3.11/site-packages  # uv python 的 site-packages
/home/yakeworld/.local/share/uv/python/cpython-3.11.../lib/python3.11/lib-dynload   # 动态加载模块
```

## 常见问题

### 1. `import PIL` 成功但 `import Pillow` 失败
```python
import PIL  # OK - 模块名
import Pillow  # FAIL - Pillow 是包名，不是模块名
```
`Pillow` 包的模块名是 `PIL`（大写）。这是历史遗留命名。

### 2. `~/.local/site-packages` 中的包无法在 venv 中使用
原因：`include-system-site-packages = false` 时，venv 完全隔离，不接触系统 site-packages。
解决：
1. 将 `pyvenv.cfg` 改为 `include-system-site-packages = true`
2. 确保 venv 的 python 能访问 `~/.local/` 中的 site-packages

### 3. dpkg 中断阻止 playwright install
```bash
sudo dpkg --configure -a
```
这是 `apt` 包管理器被中断后的常见状态。

## 完整修复流程

```bash
# 1. 确认 venv 配置
cat ~/.venv/pyvenv.cfg

# 2. 确认 venv python
ls -la ~/.venv/bin/python3
~/.venv/bin/python3 -c "import sys; print(sys.executable); print(sys.prefix); print(sys.path)"

# 3. 如果 include-system-site-packages = false，改为 true
echo 'include-system-site-packages = true' > ~/.venv/pyvenv.cfg

# 4. 如果 uv python 的 python 不在 venv 的 bin 下，创建 symlink
ln -sf ~/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3 ~/.venv/bin/python3
ln -sf ~/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 ~/.venv/bin/python3.11

# 5. 验证
~/.venv/bin/python3 -c "
import weasyprint; print('weasyprint:', weasyprint.__version__)
from PIL import Image; print('Pillow: OK')
import numpy; print('numpy:', numpy.__version__)
"
```
