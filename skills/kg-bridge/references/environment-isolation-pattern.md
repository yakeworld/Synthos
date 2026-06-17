# Environment Isolation Pattern

## 问题诊断

Agent 的 execute_code 运行在隔离 venv 中，而工具库（AKNE、jieba、sentence-transformers）安装在系统 Python 上。

### 判断方法

```python
# 在 execute_code 中运行
import sys
print(f"venv python: {sys.executable}")  # /home/yakeworld/.hermes/hermes-agent/venv/bin/python3
print(f"system python: {subprocess.run(['which', 'python3']).stdout}")  # /usr/bin/python3
```

### venv 状态

- Python 版本：3.11.15（uv 管理）
- `include-system-site-packages = false`（隔离）
- 总大小：970MB
- 已安装：networkx 3.6.1（通过 `uv pip install`，~2MB）

### 系统 Python 状态

- Python 版本：3.12.3
- 已安装：jieba 0.42.1、sentence-transformers 5.4.1、sklearn、networkx 3.6.1
- AKNE 目录：`/media/yakeworld/sda2/academic_writer/yakeworld/akne`

## 解决方案

### 方案 1：terminal 工具（推荐）

所有 AKNE 查询通过 terminal 工具执行，使用系统 Python 3.12：

```bash
terminal: akne-query.sh simple "BPPV"
terminal: akne-query.sh full "半规管"
terminal: akne-query.sh stats
```

### 方案 2：execute_code 走 venv（仅逻辑处理）

execute_code 仅用于无外部依赖的 Python 脚本（字符串处理、JSON 解析、数学计算）：

```python
# execute_code 中可运行的代码
import json, os, math, re
# networkx 也可运行（已安装）
import networkx as nx
```

### 方案 3：不要做的

- 不要尝试 `pip install` 大型包到 venv（torch 500MB+，venv 会膨胀到 1.5GB+）
- 不要在 execute_code 中 import AKNE（`ModuleNotFoundError: No module named 'akne'`）
- 不要假设系统包在 venv 中可用

## 实际案例

### 失败：execute_code import AKNE

```
File "/media/yakeworld/sda2/academic_writer/yakeworld/akne/graph/__init__.py", line 1, in <module>
    from akne.graph.graph_index import KnowledgeGraph, EntityNode
ModuleNotFoundError: No module named 'akne'
```

原因：AKNE 包不在 venv 的 `sys.path` 中。`include-system-site-packages = false`。

### 失败：execute_code import networkx（初期）

```
ModuleNotFoundError: No module named 'networkx'
```

原因：networkx 安装在系统 Python 3.12 的 site-packages，不在 venv 3.11 中。
修复：`uv pip install --python <venv_python> networkx`（30ms 安装）。

### 成功：terminal 工具执行 AKNE

```bash
terminal: python3 -c "
import sys; sys.path.insert(0, '/media/yakeworld/sda2/academic_writer/yakeworld')
from akne.graph.graph_index import KnowledgeGraph
kg = KnowledgeGraph('/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/graph.json')
print(f'Nodes: {len(kg.graph.nodes())}')  # 1475
"
```

## 通用原则

1. **先诊断**：检查 `sys.executable` 和 `which python3`
2. **再选择工具**：重型依赖 → terminal，轻量逻辑 → execute_code
3. **不要硬编码路径**：用脚本管理路径（`akne-query.sh` 封装所有路径）
4. **环境差异是常态**：不要假设 venv 和系统 Python 一致