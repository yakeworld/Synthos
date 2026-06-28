# Notebook ↔ Code ↔ Paper 对齐审计

## 问题
论文的 `.ipynb` 有时不包含最终实现代码，只是迭代中间版本。真正的实验代码可能在：
- `03-code/experiments/run_*.py` 子目录
- 同一目录下的 `*_generalization.py` 等独立脚本
- `academic_writer/` 原始开发目录（含完整迭代历史）

## 审计步骤

### 1. 检查 notebook 是否包含核心实现
```python
keywords = ['HCS-3WT', 'Expert A', 'Expert B', 'Expert C', 'Arbiter',
            'cascade', 'triple_product', 'BorderlineSMOTE',
            'LOW_THRESHOLD', 'HIGH_THRESHOLD', 'VotingClassifier']
# 如果关键词计数为0 → notebook 不是最终实现
```

### 2. 找到真正的实验代码
```bash
# 搜索关键实现
find . -name "*.py" -exec grep -l "HCS-3WT\|Expert A\|Expert B\|Expert C" {} \;
# 或
find . -name "run_*.py" -type f
```

### 3. 对比 notebook 和代码目录
| 检查项 | 期望 |
|:-------|:-----|
| Notebook 有执行输出 | ✅ 每个 code cell 有 outputs |
| Notebook 包含完整流程 | ✅ 从数据→预处理→训练→评估→结果 |
| Notebook 和脚本 md5 一致 | ✅ 同一份代码 |
| experiments/ 有对应 JSON | ✅ 结果可追溯 |

### 4. 修复方案
- **方案A**：将最终实现代码完整迁移到 notebook 中，保留执行输出
- **方案B**：在 notebook 中通过 `exec()` 或 `%run` 调用实验脚本，保留调用链
- **方案C**：在 `07-quality` 目录记录审计发现，标注"notebook 非最终实现，代码在 experiments/ 中"

## 典型错误模式
- Notebook 只有传统 ML 基线（如 13 个 sklearn 模型），没有 HCS-3WT 级联
- Notebook 没有执行输出（所有 cell outputs 为空）
- `03-code/` 下有 notebook，`03-code/experiments/` 下有 Python 脚本，但两者独立，未建立链接
- 同一论文在 `academic_writer/` 和 `Synthos/outputs/papers/` 各有不同版本

## 铁律
> 代码+数据+JSON输出必须全部归档到 03-code/。Notebook 必须包含完整可复现流程（含输出），否则视为质量不合格。
