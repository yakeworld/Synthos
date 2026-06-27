# 图生成输出路径陷阱

> 2026-06-27，HCS-3WT Figure 1 重写时出现

## 问题

当生成脚本位于 `03-code/` 子目录时，`output` 参数使用 `05-figures/...` 相对路径，实际输出到 `03-code/05-figures/` 而非论文根目录的 `05-figures/`。

**原因**：`os.path.dirname(os.path.abspath(__file__))` 获取的是脚本所在目录（`03-code/`），路径拼接后变成 `03-code/05-figures/`。

## 修复方案

**方案 1**：在脚本中使用双 `dirname` 获取论文根目录：
```python
OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**方案 2**：argparse `--output` 默认路径使用 `../` 相对路径：
```python
parser.add_argument("--output", default="../05-figures/fig1_system_architecture.svg", ...)
```

## 验证

生成后必须 `ls -la 05-figures/` 确认输出在正确位置。

**教训**：脚本被 Codex 修改后，输出文件可能不更新，因为写入到了错误路径。发图前必须检查时间戳和路径。