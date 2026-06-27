# 乳腺癌论文 HCS-3WT 作图审计 — 实战案例

**论文**: HCS-3WT for Breast Cancer Diagnosis  
**目录**: `/media/yakeworld/sda2/Synthos/outputs/papers/hcs3wt-breast-cancer/`  
**审计日期**: 2026-06-27  

## 审计过程

### 1. 铁律检查：图↔脚本映射
- 6张图（fig1-6），6个生成脚本 → 全部通过

### 2. 铁律检查：脚本可运行
- 初始状态：4/6 运行成功
- fig2: `KeyError: 'n_folds'` → 改为 `results['n_splits']`
- fig2: `AttributeError: 'Figure' object has no attribute 'inset_axes'` → 改为 `fig.add_axes()`
- fig6: `FileNotFoundError: hcs3wt_teaching_results.json` → 相对路径改为完整路径
- 修复后：6/6 全部通过

### 3. 铁律检查：数据诚信
发现 2 个硬编码数据问题：
- **fig3** (confusion_matrices.py): 模型性能数据硬编码在第33-38行
  ```python
  models_data = {
      'LR': {'auc': 0.9897, 'accuracy': 0.9360, ...},
      'CatBoost': {'auc': 0.9881, 'accuracy': 0.9438, ...},
      ...
  }
  ```
  数据与 `experiment_results.json` 一致，但脚本未引用该文件。
  
- **fig4** (feature_importance.py): 特征重要性硬编码在第18-23行
  ```python
  FEATURE_IMPORTANCE = [
      ('worst_radius', 0.285), ('worst_perimeter', 0.142), ...
  ]
  ```

### 4. QA检查
- fig1: 完整 QA 类 `FigureGenerator` 包含 `check_text_fits`, `check_arrow_inside`, `check_arrow_crosses_box`, `check_boundary`
- fig1 运行 QA 后输出: "QA CLEAN — no issues"
- fig2-6: 无独立 QA 检测

### 5. 文件有效性
18个文件（6图 × 3格式）全部通过头检查：
- PNG: 头 `89504e47` ✅
- PDF: 头 `%PDF` ✅  
- SVG: 头 `<?xm` ✅

### 6. LaTeX引用检查
- 仅 fig1 在 `.tex` 中被引用（`includegraphics`）
- fig2-6 未被引用 — 属于论文正文缺失问题

## 修复方案

### fig3 硬编码修复
```python
# 改为从 experiment_results.json 读取
with open(os.path.join(script_dir, 'experiment_results.json')) as f:
    results = json.load(f)
models_data = {k: v for k, v in results['single_models'].items()}
n_pos = results['n_malignant']  # 212
n_neg = results['n_benign']     # 357
```

### fig4 硬编码修复
```python
# 改为从 experiment_results.json 读取
with open(os.path.join(script_dir, 'experiment_results.json')) as f:
    results = json.load(f)
rf_data = results['single_models']['RF']
feature_importance = rf_data.get('feature_importance', [])
```

## 经验教训

1. **硬编码检测需要多层规则** — 单靠 `json` 关键词不够，需要检测具体的硬编码模式
2. **相对路径是常见 bug 来源** — 永远用 `os.path.dirname(os.path.abspath(__file__))` 构建路径
3. **matplotlib API 版本兼容性** — `fig.inset_axes()` 在 3.4+ 才有，旧版用 `fig.add_axes()`
4. **数据键名可能变化** — `n_folds` vs `n_splits`，脚本应容错处理或明确文档化
