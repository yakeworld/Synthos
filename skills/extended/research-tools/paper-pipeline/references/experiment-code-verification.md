# 实验代码验证工作流（L0.5前置）

> 2026-05-26 实战形成：hcs3wt-breast-cancer

## 何时触发

论文目录下有实验代码（`experiment/*.py`、`*.ipynb`）和/或结果文件（`*.json`、`*.csv`），但论文数值与实验数据不一致时。

## 完整工作流

### Phase 1: 代码审查（先审再跑）

不要盲信已有的 JSON/CSV 结果文件。代码可能有 bug，导致结果不可靠。

```bash
# Step 1: 理解实验设计
head -50 experiment/*.py | grep -E 'dataset|n_samples|n_features|load|split|CV'
grep -n 'fn_red\|hcs_fn\|auto_rate\|automation\|accuracy\|recall' experiment/*.py

# Step 2: 检查已知bug模式
grep -n 'for.*in.*models.*:' experiment/*.py  # 循环变量泄露
grep -n 'X_test_raw\|X_train_raw' experiment/*.py  # 变量名不一致
grep -n 'SMOTE\|smote\|fit_resample' experiment/*.py  # SMOTE位置
grep -n 'fn_reduction\|fn_red.*=' experiment/*.py  # FN计算逻辑
```

**2026-05-26 实战发现的3类bug：**
1. **变量名拼写错误**：`X_test_raw` 未定义（应为 `X_test`）
2. **SMOTE 位置错误**：应用到部分特征集而非完整特征集
3. **循环变量泄露**：`for name in models` 后 `name` 指向最后一项而非取 min

### Phase 2: 运行实验获取真实数据

```bash
cd experiment/
python3 run_*.py 2>&1 | tee experiment_output.txt
grep -E 'auto_rate|fn_reduction|automation' experiment_output.txt
```

### Phase 3: 逐数值对比

```bash
# 论文声称
grep -oP '[0-9]+\.[0-9]+%|fn.*[0-9]|automation.*[0-9]' ../paper.tex | sort -u

# 实验数据
python3 -c "
import json
d = json.load(open('experiment_results.json'))
h = d['hcs3wt']
print(f'Auto rate: {h[\"automation_rate\"]}%')
print(f'FN reduction: {h[\"fn_reduction_pct\"]}%')
print(f'HCS FN: {h[\"hcs_fn\"]} vs Best Single FN: {h[\"best_single_fn\"]}')
"
```

### Phase 4: 方向性检查

不检查数值大小，更要检查**方向**：

| 论文声称 | 实验 fn_reduction | 判定 |
|:---------|:-----------------:|:-----|
| "FN decreased 67%" | > 0 | ✅ 方向一致 |
| "FN decreased 67%" | < 0 | 🔴 **方向相反** |

2026-05-26 hcs3wt: 论文声称-67%，三个独立实验全部显示 -28% 到 -47.7%（FN增加）

### Phase 5: 叙事重定位

当实验不支持预期时，从"错误减少"转向"不确定性集中"：

```
❌ "HCS-3WT reduces false negatives by 67%"
✅ "HCS-3WT achieves 1.22x malignant enrichment in the Gray Zone"
```

### Phase 6: 更新论文

1. 用真实数值替换 Abstract/Results/Tables/Discussion
2. 添加 10x5 CV 标准差
3. 添加 L0.5 数据诚实声明表
4. 如实讨论 FN 不降的原因
5. 再跑双质检

## 快速检测命令

```bash
# 检查LLM典型虚高标记
grep -oP '84\\.76|67%|100%|99\\.99|0\\.99[0-9]{2}' paper.tex

# 检查实验文件存在性
find experiment/ -name '*.json' | head -5

# 一键FN方向检查
python3 -c "
import json, glob
jsons = glob.glob('experiment/*.json')
if jsons:
    d = json.load(open(jsons[0]))
    h = d.get('hcs3wt', d)
    fn_r = h.get('fn_reduction_pct', 0)
    tex = open('paper.tex').read()
    if fn_r < 0 and 'reduc' in tex.lower():
        print('🔴 Paper claims reduction but experiment shows increase!')
    print(f'Auto: paper={[m for m in __import__(\"re\").findall(r\"[0-9]+\\.[0-9]+%\",tex)[:3]]} expt={h.get(\"automation_rate\",\"?\")}%')
"
```
