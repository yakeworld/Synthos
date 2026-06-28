# diagnose.py 已知的检测盲区

## 盲区 1: git staged deletes (`D`) 对 dirty count 的影响

`git status --porcelain` 返回的 dirty count 包含所有状态：
- ` M` — 修改（unstaged）
- `M ` — 修改（staged）
- ` D` — 删除（staged）
- `??` — 未跟踪

但 PROBE 步骤只计算 `total_dirty = len(dirty_lines)`，不区分类型。
这意味着 567 个 staged deletes 和 5 个 modified files 被计为同等 572 dirty files。

**影响**：absorption = 1.0 - (total_dirty / total_skills) 会被严重拉低。
structural 的 dirty_penalty = (total_skills - dirty_sk) / total_skills 也受影响。

**修复**：在 PROBE 步骤中，区分 dirty 类型：
```python
staged_deletes = len([l for l in dirty_lines if l.startswith('D ')])
modified = len([l for l in dirty_lines if ' M' in l or l.startswith('M ')])
untracked = len([l for l in dirty_lines if l.startswith('??')])
```

对 absorption 计算使用更精确的公式：
```python
# Don't penalize for staged deletes — they are intentional
absorption = 1.0 - (modified / total_skills)
```

## 盲区 2: WARNING 不自动触发 re-benchmark

`self_deception_risk` 检测只在 diagnose.py 的最后打印 WARNING，
但后续代码不会自动触发 re-benchmark。需要手动干预。

**修复**：在 evolve 流程中，每次运行 diagnose.py 后检查输出中是否有 WARNING，
如果有则自动进入 re-benchmark 流程。

## 盲区 3: 嵌套 YAML 前导键检测

`grep "^version:"` 会漏掉嵌套在 `metadata.synthos:` 下的前导键。
当前 diagnose.py 使用 Python yaml.safe_load() 解析，这比 grep 准确得多，
但仍需注意：grep 用于检测 IO_CONTRACT（正文中）时使用正确，
但 grep 用于检测 version/signature（前导中）时可能不准确。

**当前状态**：diagnose.py 使用 yaml.safe_load() 检测 version/signature，已修复此问题。
但 benchmark 步骤中 `if 'signature' in content.lower()` 是全文搜索（包括正文），
可能导致 false positive。建议改为只在前导 YAML 区域搜索。
