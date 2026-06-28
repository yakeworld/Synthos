# 多实验脚本输出交叉验证

> 2026-06-23 实战产出 — PIMA论文实验审计教训

## 问题

论文 `03-code/` 目录下可能存在多个实验脚本，每个产生不同的 JSON/CSV 输出。paper.tex 的数值可能来自：
- 其中某个脚本的中间输出（后被覆盖）
- 不存在于任何脚本的虚构值
- 多个脚本结果的混用

## 检测流程

### Step 1: 枚举所有实验脚本

```bash
find <paper_dir>/03-code/ -name "*.py" | sort
```

### Step 2: 追踪每个脚本的输出文件

对每个 `.py` 脚本，提取其最后的写入/保存操作：
```bash
# 查找 JSON/CSV 写入操作
grep -n 'to_json\|to_csv\|\.save\|dump(' script.py
```

### Step 3: 收集所有输出文件中的 actual_values

```python
import json, glob

outputs = {}
for f in glob.glob('experiment/results/*.json'):
    with open(f) as fh:
        data = json.load(fh)
    # 提取所有数值字段，忽略 metadata/notes
    vals = {}
    for k, v in flatten(data).items():
        if isinstance(v, (int, float)) and not k.endswith('_note'):
            vals[k] = v
    outputs[f] = vals

# 与 paper.tex 对比
paper_values = {}  # 从 paper.tex 提取
for key, paper_val in paper_values.items():
    found_in = []
    for f, vals in outputs.items():
        if abs(vals.get(key, -1) - paper_val) < 0.001:
            found_in.append(f)
    if not found_in:
        print(f"[DATA_FABRICATED] {key}={paper_val} not in any experiment output")
```

### Step 4: 区分 paper_claims 和 actual_values

某些 JSON 输出（如 definitive_ablation.json）同时包含 paper_claims（论文中写的值）和 actual_values（实际测量值）。**必须核对 actual_values**，而非 paper_claims。

```python
# 错误做法 — 用 paper_claims 验证论文：
paper_claims = data.get('paper_claims', {})  # 这些值本身就是伪造的！

# 正确做法 — 用 levels/actual_values 验证论文：
actual = data.get('actual_values') or flatten(data.get('levels', {}))
```

## PIMA案例

| 脚本 | 输出文件 | severe_leakage.f1 | severe_leakage.recall |
|:-----|:---------|:-----------------:|:---------------------:|
| pima_definitive.py | definitive_ablation.json (levels) | 0.6451 | 0.6232 |
| pima_definitive.py | definitive_ablation.json (paper_claims) | 0.7338 | 0.7080 |
| pima_crispdm_helix.py | ablation_v3.json | 0.6520 | 0.6398 |
| **paper.tex** | **无** | **0.6661** | **0.5030** |

paper.tex 的 severe_leakage 值（recall=0.5030, precision=1.0000）**不在任何实验输出中** → 彻底虚构。
