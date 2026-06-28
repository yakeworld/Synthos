# 糖尿病相关公开数据集参考

**最后更新**: 2026-06-21

## 推荐数据集（按推荐度排序）

| 排名 | 数据集 | 样本 | 特征 | 来源 | OpenML ID | 说明 |
|:-----|:-------|:-----|:-----|:-----|:----------|:-----|
| 1 | PIMA Indians Diabetes (PIDD) | 768 | 8 | UCI | 292 | 当前论文已用，经典基线 |
| 2 | PIMA Indians Diabetes v2 | 768 | 8 | UCI | - | 同 PIDD 同源但独立发布 |
| 3 | PhysioNet INSCAT Diabetes | 300 | 8 | PhysioNet | - | 印度心脏病研究中心，真实临床随访 |
| 4 | Diabetes 130-US Hospitals | 8200 | 12 | UCI | - | 美国 130 家医院，更真实 |
| 5 | Australian Diabetes | 500 | 10 | AIHW | - | 澳大利亚人群，验证种族泛化 |
| 6 | NHANES Diabetes | 3000 | 10 | CDC | - | 全国健康调查，代表性最强 |

## sklearn 可访问的数据集

```python
from sklearn.datasets import fetch_openml

# 验证可用的数据集
datasets = [
    "pima-indians-diabetes",      # PIMA 原始
    "pima-indians-diabetes.v2",   # PIMA v2
    "breast-cancer",              # 乳腺癌
    "breast-cancer-wisconsin",    # 乳腺癌 Wisconsin
    "breast-cancer-coimbra",      # Coimbra 乳腺癌
    "heart-disease",              # 心脏病
    "diabetes",                   # 糖尿病
]

for name in datasets:
    try:
        ds = fetch_openml(name=name, version=1, as_frame=True, parser='auto')
        print(f"OK {name}: {ds.data.shape[0]} samples, {ds.data.shape[1]} features")
    except Exception as e:
        print(f"FAIL {name}: {str(e)[:60]}")
```

## 论文应用建议

### Pima 论文加数据集方案

```
论文结构不变（方法论审计为主线）
├── 实验 1: PIDD（完整方法论审计 + 32 基线 + 消融）— 不变
├── 实验 2: WDBC（同方法论，32 基线 + 最优模型）— 新增
├── 实验 3: 对比实验 — PIDD vs WDBC 的最优模型性能对比 — 新增
└── 讨论：方法论在不同领域的泛化能力 — 新增
```

### 三层论证链

1. **PIDD** — 方法论验证（方法正确性）
2. **PhysioNet INSCAT** — 种族泛化（印度人群 vs 美国 PIMA）
3. **Diabetes 130-US** — 规模+真实性（美国大型医院）

## 注意事项

1. OpenML 数据集名称格式：`fetch_openml(name="pima-indians-diabetes", version=1)` — 不是 `name="pima"`
2. 验证数据集可访问性后再写入论文
3. 所有实验必须使用相同的随机种子（random_state=42）
4. 所有预处理必须在每个 fold 内独立完成（防止数据泄露）