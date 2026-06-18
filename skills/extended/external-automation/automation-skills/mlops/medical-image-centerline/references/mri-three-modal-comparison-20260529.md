# 三模态中心线拟合对比（CT vs uCT vs MRI）

## 数据来源

| 模态 | CSV文件 | 数量 | 管线 |
|:----|:--------|:----:|:----|
| **CT** | `batch_logspiral_params_A_manual.csv` | 480行 (160例×3管) | UNet分割+v5中心线管线 |
| **uCT HBL** | `batch_logspiral_params_HBL_uCT_v5.csv` | 186行 (62耳×3管) | v5管线 (rejection_ratio=0.40) |
| **MRI semical** | `batch_logspiral_params_MRI.csv` | 489行 (163例×3管) | v5管线 (rejection_ratio=0.40) |

## 批量提取命令

```bash
cd /media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/code
python3 -u batch_mri_centerlines_v2.py
```

163/164 成功（1例失败可能因空标签），~10min完成。

## 拟合速度演化

| 版本 | 方法 | 时间 | 结论 |
|:----|:-----|:---:|:----|
| v1 | 3阶段Nelder-Mead (16×3000+10000 iter/管) | ~40s/管 → 5.5h/全量 | ❌ |
| **v2** | SVD平面+线性LSQ+轻量Nelder-Mead (2000 iter) | **~2s/管 → 10min/全量** | **✅** |

## 完整统计输出

```
━━━━ MRI (n=489) ━━━━
  superior: |b|=0.0514±0.0379 median=0.0472  arc=7.9±2.3  rmse=0.6488
  posterior: |b|=0.0485±0.0379 median=0.0453  arc=7.4±2.2  rmse=0.6258
  lateral: |b|=0.0335±0.0346 median=0.0200  arc=8.0±2.8  rmse=0.7376

━━━━ uCT HBL (n=186) ━━━━
  superior: |b|=0.1936±0.2277 median=0.0934  arc=8.3±2.7  rmse=0.0521
  posterior: |b|=0.1878±0.1953 median=0.1284  arc=7.6±2.5  rmse=0.0471
  lateral: |b|=0.2603±0.2663 median=0.2094  arc=6.4±1.8  rmse=0.0349

━━━━ CT (n=480) ━━━━
  superior: |b|=0.1863±0.2728 median=0.0349  arc=10.5±3.0  rmse=0.0890
  posterior: |b|=0.1988±0.3176 median=0.0622  arc=9.7±4.6  rmse=0.0724
  lateral: |b|=0.2132±0.2896 median=0.1023  arc=7.5±2.3  rmse=0.0502
```

## Mann-Whitney 检验

```
MRI vs CT:  AC p=0.011  PC p<0.001  LC p<0.001   ❌ 显著差异
MRI vs uCT: AC p<0.001  PC p<0.001  LC p<0.001   ❌ 显著差异
uCT vs CT:  AC p=0.26   PC p=0.20   LC p=0.08    ✅ 不显著 (模态无关)
```
