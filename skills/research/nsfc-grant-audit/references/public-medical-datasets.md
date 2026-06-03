# 公开医学影像数据集检索

> 2026-05-21 创建
> 场景：评审涉及CT/MRI数据 + ML的标书时，查公开数据集可补充或验证研究方案
> 触发条件：Proposal涉及医学影像 + 机器学习/深度学习

## 检索策略（三层递进）

```
Level 1 — PubMed
  Query: ("dataset" OR "public dataset" OR "benchmark") AND (anatomy) AND (imaging)
  Limit: >= 2020, English
Level 2 — Zenodo / Figshare
  Direct keyword search on open repositories
Level 3 — GitHub
  Search: <anatomy> + "dataset" or "segmentation" or "benchmark"
```

### PubMed E-utilities 脚本框架

```python
import requests, time, json

def search_pubmed(title_terms, author, year):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f'({title_terms}) AND {year}[Date - Publication]',
        "retmode": "json",
        "retmax": 20
    }
    r = requests.get(base, params=params, timeout=10)
    return r.json()
```

## 已知数据集目录

### 鼻窦 / 头颈

| 数据集 | 托管 | 规模 | 内容 | 标注 | 许可证 |
|:-------|:-----|:-----|:-----|:------|:-------|
| NasalSeg | Zenodo (13893419) | 130 CT | 鼻腔+上颌窦+鼻咽 | 像素级5结构分割 | 开源免费 |
| CMF Defects | Figshare | ~100 CT | 颅颌面缺损 | 修复分割 | 开源 |

### 胸部

| 数据集 | 托管 | 规模 | 内容 | 标注 |
|:-------|:-----|:-----|:-----|:------|
| ChestX-ray14 | NIH | 112K X-ray | 14种胸部疾病 | 图像级标签 |
| LUNA16 | 官网 | 888 CT | 肺结节检测 | 结节标注 |

### 腹部

| 数据集 | 托管 | 规模 | 内容 | 标注 |
|:-------|:-----|:-----|:-----|:------|
| Medical Segmentation Decathlon | 官网 | 10 tasks | 多器官 | 分割 |
| KiTS | Zenodo | 300+ CT | 肾脏肿瘤 | 分割 |

### 眼科

| 数据集 | 托管 | 规模 | 内容 |
|:-------|:-----|:-----|:-----|
| EyePACS | Kaggle | 88K | 糖尿病视网膜病变 |

## 坑

1. FBS（真菌球型鼻窦炎）无专用公开数据集。所有AI研究均用机构私有数据。标书必须自建病例队列。
2. NasalSeg只有正常解剖分割，无疾病标签。适合做健康对照组解剖参数基线，不可替代病例组。
3. PLoS One等期刊有Data Availability Statement，搜索"data are available" + topic可定位开放数据集论文。
4. GitHub找到repo不等于找到可下载数据——很多只是代码，数据仍需申请。
