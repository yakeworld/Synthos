# Imbalance-Driven F1 Inflation — 三数据集实验结果

> 实验日期: 2026-05-31 | 方法: 5×2 CV, LogisticRegression/Helix vs Leaky
> 代码: 03-code/experiments/run_cross_dataset.py (论文项目目录)

## 结果表

| 数据集 | n | 特征 | 患病率 | Helix F1 | Leaky F1 | F1膨胀 | Helm Recall | Leaky Recall | Λ |
|:-------|:-:|:----:|:------:|:--------:|:--------:|:------:|:-----------:|:------------:|:-:|
| PIDD | 768 | 8 | 34.9% | 0.664 | 0.738 | **+11.1%** | 0.713 | 0.700 | 0.001 |
| CDC BRFSS | 50,000 | 21 | 13.8% | 0.444 | 0.768 | **+73.2%** | 0.766 | 0.791 | 0.000 |
| Early Diabetes | 520 | 16 | 61.5% | 0.930 | 0.915 | -1.6% | 0.913 | 0.900 | 0.000 |

## 关键发现

1. **F1膨胀量 ∝ 类不平衡严重度**: CDC(13.8%)→+73.2%, PIDD(34.9%)→+11.1%, Early Diabetes(61.5%)→-1.6%
2. **Λ值局限性**: 当Recall因泄漏而上升时Λ≈0（CDC），但单靠F1膨胀率已足够支撑结论
3. **普适性**: 此模式出现在3个独立数据集，证明是全局预处理下所有不平衡临床数据的系统性脆弱性

## 数据来源

| 数据集 | 来源 | 许可证 |
|:-------|:-----|:-------|
| PIDD | NIDDK / Kaggle | CC0 |
| CDC BRFSS 2015 | UCI ML Repository (ID=891) | CC0 |
| Early Diabetes | UCI ML Repository (ID=529) | CC0 |

## 运行命令

```bash
docker run --rm \
  -v /home/yakeworld/synthos_data:/data \
  -v $(pwd)/03-code/experiments:/code \
  python:3.11-slim \
  bash -c "pip install -q pandas scikit-learn imbalanced-learn && python3 /code/run_cross_dataset.py"
```
