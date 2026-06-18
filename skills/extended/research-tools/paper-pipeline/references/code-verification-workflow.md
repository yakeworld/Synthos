# 代码验证优先工作流 (Code-First Verification Workflow)

> 2026-05-26 实战提炼
> 适用于：论文目录包含实验代码时，L0.5 数据诚实门的执行方案

## 核心原则

**不要信任 LLM 生成的论文数值，即使它们看起来合理。** 实验 JSON 文件在手边也不够——代码本身可能有 bug，必须先审查代码再运行。

## 六步验证流程

```
论文声称数值
  ↓
Step 1: 定位代码
  搜索 experiment/*.py, *.ipynb, run_*.py
  ↓
Step 2: 审查代码逻辑 ← 关键步骤
  检查数据加载、预处理、训练、评估各环节
  ↓
Step 3: 修复 bug
  变量名错误、SMOTE顺序、指标计算等
  ↓
Step 4: 运行实验
  python3 run_*.py  10×5 CV (约2分钟)
  ↓
Step 5: 对比论文声明 vs 实验输出
  逐行逐数字对比
  ↓
Step 6: 用真实数据重写论文
  诚实报告，必要时重构叙事
```

## Step 2 审查清单

| 检查项 | 问什么 | HCS-3WT实战发现 |
|:-------|:-------|:----------------|
| 数据加载 | 数据集是否匹配论文声称？ | 论文称 WBC Original (699×9)，代码有时跑 WDBC (569×30) |
| 预处理泄漏 | 标准化/SMOTE/特征选择是否在训练集内fit？ | SMOTE应用到错的特征子集 |
| 变量名 | 测试/训练变量是否混淆？ | `X_test_raw` → `X_test` 拼写错误 |
| 指标计算 | 正类标签是否匹配？FN怎么算的？ | `best_single_fn`用错了循环变量名 |
| 方向验证 | 声称的"改善"在JSON中是否为正数？ | 声称67%减少，JSON输出-47.7%（方向反） |

## Step 5 对比模板

```python
import json, re

# 提取论文声明
with open('paper.tex') as f:
    tex = f.read()

# 提取实验JSON
with open('experiment/experiment_results.json') as f:
    exp = json.load(f)

checks = {
    'automation_rate': (r'84\.76|79\.07|automation.*?rate', 'hcs3wt.automation_rate'),
    'fn_reduction': (r'67%|-28%|fn.*?reduction', 'hcs3wt.fn_reduction_pct'),
    'accuracy': (r'0\.9571|0\.9657|overall.*?accuracy', 'hcs3wt.hcs_accuracy'),
}
for metric, (tex_pat, exp_path) in checks.items():
    tex_match = re.search(tex_pat, tex, re.IGNORECASE)
    exp_val = exp
    for key in exp_path.split('.'):
        exp_val = exp_val.get(key, {}) if isinstance(exp_val, dict) else None
    print(f'{metric}: paper={tex_match.group(0) if tex_match else "N/A"} json={exp_val}')
```

## Step 6 叙事重构策略

当实验不支持论文预期时，不要强行维持原叙事。常见的重构模式：

| 原叙事 | 真实数据 | 重构叙事 |
|:-------|:---------|:---------|
| "减少67%假阴性" | FN reduction = -28% | "灰区恶性富集1.22×，将临床不确定性集中在高风险病例" |
| "超越SOTA" | 与单分类器相当 | "提供等效分类性能下的不确定性管理机制" |
| "100%自动化准确率" | 99.35% | "近乎完美但非零错误的自动化区域" |

**核心原则**：诚实的结果 + 有趣的重构 > 华丽的虚假声明。复查Reviewer也能运行代码验证。
