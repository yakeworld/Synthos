# UCI数据集下载指南

## URL模式

UCI机器学习库的下载URL已迁移到静态目录。

### 旧模式（可能404）
```
https://archive.ics.uci.edu/ml/machine-learning-databases/<dataset>/<file>
https://archive.ics.uci.edu/ml/datasets/<dataset>
```

### 新模式（当前有效）
```
https://archive.ics.uci.edu/static/public/<ID>/<dataset>.zip
```

### 查找正确ID的方法
1. 访问数据集页面（可能跳转React前端）
2. 解析页面HTML中的 `href="/static/public/ID/文件名"`
3. 或直接访问 `https://archive.ics.uci.edu/ml/datasets/<dataset>` 查找链接

## 已知数据集映射

| 数据集 | 静态目录ID | 原始数据集目录 |
|:-------|:-----------|:---------------|
| Liver Disorders | 60 | liver-disorders |
| Thyroid Disease | 102 | 00140 |
| Chronic Kidney Disease | 336 | 00251 |
| Pima Diabetes | N/A (通过Kaggle镜像) | pima-indians-diabetes |
| Breast Cancer | N/A (UCI原始URL仍有效) | breast-cancer-wisconsin |
| Cleveland Heart | N/A (UCI原始URL仍有效) | heart-disease |

## 格式注意事项

UCI数据集可能返回多种格式：
- **ZIP** → 需解压，内部可能是RAR（嵌套压缩）
- **RAR** → 需`unrar`或`7z`解压
- **ARFF** (Weka格式) → 需转CSV
- **DATA** (UCI原始) → 逗号分隔但无表头，需手动加表头

## 常见镜像源

当UCI直接下载失败时，尝试：
- Kaggle镜像: `https://raw.githubusercontent.com/...`
- HuggingFace: `https://huggingface.co/datasets/...`
- GitHub公开仓库: `https://raw.githubusercontent.com/...`
