# Fabrication Detection Patterns

## Core Principle

> 凡数必源。论文中每个数值声明必须能追溯到代码输出文件。
> 无代码输出支撑的数值 = 直接伪造。
> 有代码输出但方法不同 = 方法混淆。

## Detection Method

For every numerical claim in the paper, verify against:
1. **Notebook cell outputs** (`.ipynb` → parse JSON)
2. **Experiment result files** (`.json`, `.csv` in `03-code/experiment/results/`)
3. **state.json** declared values (cross-check with code)
4. **Table values** in paper vs actual experiment results

## Common Fabrication Patterns

### Pattern 1: Direct Fabrication (无代码支撑)
The value never appears in any code output, notebook, or result file.
```
论文声称: Severe Leakage → F1=0.8140
实际代码: 无任何输出文件包含 0.8140
检测: 遍历所有 result JSON/CSV 文件，grep 该值 → 无匹配 → 伪造
```

### Pattern 2: Method Confusion (方法混淆)
The value exists in code output but from a different method than described.
```
论文描述: "Pipeline + cross_validate" 方法产生 F1=0.6878
实际: Cell 24 用 imblearn.pipeline.Pipeline → F1=0.6878 ✓
      helix_benchmark.py 用手动 folds + soft voting → F1=0.6360 ✗
```

### Pattern 3: Numeric Drift (数值漂移)
The value is close but not exact.
```
论文声称: GradientBoosting Acc=0.7875
实际代码: GradientBoosting Acc=0.7616
差异: +0.026 (1.5个标准差外) → 可能为手工调整
```

### Pattern 4: Selective Reporting (选择性报告)
Only the "good" values are reported, omitting worse outcomes.
```
论文报告: No Leakage → Severe Leakage 各层级 F1 单调递增
实际: 轻度泄露仅+0.6%，重度泄露F1反而下降
```

### Pattern 5: Fabricated Contextual Data (伪造上下文数据)
Numerical claims about external literature that cannot be verified.
```
论文: "BRFSS under proper CV, highest AUC = 0.718-0.795 [Xiong2019BRFSS]"
Xiong2019BRFSS 条目: 无期刊、无年份、无DOI → 伪造引用
```

## Verification Checklist

Before concluding any value is fabricated, run these checks:

1. [ ] Searched all `.json` files in the paper's `03-code/` directory
2. [ ] Searched all `.csv` files in the paper's `03-code/` directory
3. [ ] Parsed the Notebook JSON for cell outputs
4. [ ] Checked `state.json` declared values
5. [ ] Searched for the exact decimal value (e.g., `0.8140`) in all files
6. [ ] Searched for nearby values (e.g., `0.81`, `0.814`) in case of rounding

## Paper Patching Protocol

After identifying fabrications, fix the paper in this exact order:

1. **Abstract** — 核心叙事 + 关键数值
2. **Figure 1** — 流程图中的描述
3. **Introduction** — 贡献列表
4. **Algorithm 1** — 伪代码
5. **Results** — 正文描述 + 所有表格
6. **Discussion** — Claim/Grounds/Warrant + 子标题
7. **Conclusion** — 总结性声明
8. **References** — 清理伪造引用条目

Each patch should:
- Use exact old_string with sufficient context
- Replace with actual experiment values
- Maintain narrative coherence (don't just swap numbers — update the story)
