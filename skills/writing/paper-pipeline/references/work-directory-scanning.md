# Work Directory 论文资产扫描

> 用户的 /home/yakeworld/work/ 目录包含大量未论文化的实验代码、手稿和数据集。
> 定期扫描可发现2-5篇新论文素材。

## 常见论文资产类型

| 类型 | 目录 | 论文潜力 | 提取方式 |
|:-----|:------|:--------:|:---------|
| Jupyter notebook | `eye/*.ipynb` | ⭐⭐⭐⭐⭐ | 提取Matlab公式+代码→Code-to-Paper |
| 论文手稿(Markdown) | `bppv/BPPV/*.md` | ⭐⭐⭐⭐⭐ | 直接转化为LaTeX+补全质检 |
| 数据集+模型 | `alzheimer/`, `pima/` | ⭐⭐⭐⭐ | CRISP-DM管线 |
| 选刊数据 | `zkyfq/*.csv` | ⭐⭐⭐ | 科研信息学 |
| 代码库 | `drug/HerbiV-main/`, `langgraph/` | ⭐⭐⭐ | 工具论文/方法论文 |

## 扫描流程

```bash
# Step 1: 目录结构
ls /home/yakeworld/work/

# Step 2: 找 notebook 和新方向
find /home/yakeworld/work/ -name "*.ipynb" -size +100k | head -30

# Step 3: 找未入库手稿
find /home/yakeworld/work/ -name "*.md" -size +10k | head -20

# Step 4: 找数据集
find /home/yakeworld/work/ -name "*.csv" -size +1M | head -10
```

## 实战记录

2026-06-05 扫描产出：
- eye/ 目录 → 130+ notebooks → 1篇3D瞳孔定位新论文 (已启动)
- bppv/BPPV/ → 8篇手稿 → 5篇新论文 (cron每日08:00入库)
- drug/HerbiV-main/ → 中医药AI新方向 (待评估)
- zkyfq/ → 21K行JCR选刊数据 (待评估)
