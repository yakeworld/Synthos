# BRFSS Literature Audit — 数据泄漏验证全流程（2026-06-03 实战）

> 本文件记录如何从文献中提取CDC BRFSS糖尿病预测基准性能数据、
> 与Helix协议结果对比、并定位方法学泄漏点的完整流程。
> 适用于任何需要跨数据集验证+文献对照的论文。

## 审计流程（可复用）

### Step 0: 确认目标数据集规格
```
数据集: CDC BRFSS 2015 (Diabetes Health Indicators)
样本量: 253,680 (二分类: 70,692; 三分类: 253,680)
特征数: 21
患病率: ~13.8% (严重不平衡)
Kaggle: alexteboul/diabetes-health-indicators-dataset
```

### Step 1: 文献检索（多源）

| 源 | 查询词 | 结果数 | 策略 |
|:---|:-------|:------:|:-----|
| OpenAlex | `BRFSS machine learning` | 1,291 | 宽查询+标题过滤 |
| Semantic Scholar | `BRFSS diabetes predict` | 0 (空) | 太具体→换宽查询 |
| OpenAlex | `BRFSS diabetes prediction` | 155 | 精确定位糖尿病论文 |

过滤条件: 标题含"diabetes" + BRFSS

### Step 2: 全文下载优先级

```
① OA直连 (PLOS ONE/MDPI/arXiv/SpringerOpen) → 优先
② Sci-Hub (curl_cffi + 域轮换) → 付费期刊
③ paper-manager download_one.py → 后备
④ 标记为PAYWALL → 无法获取
```

**本实战成功下载**:
| 论文 | DOI | 路径 | 方法 |
|:-----|:----|:-----|:-----|
| Shams2025 | 10.1186/s43067-023-00074-5 | SpringerOpen直连 | `curl -sL` |
| Li2024 | 10.1371/journal.pone.0311222 | PLOS ONE直连 | `curl -sL "journals.plos.org/.../file?id=..."` |

### Step 3: 全文方法学验证（关键）

定位方法学错误的**三步检测法**:

```python
# 对每篇下载的PDF全文:
# 1. 提取预处理步骤的顺序描述
grep -n -i "train.test.split\|SMOTE\|upsampl\|preprocess\|80.*20\|cross.val" paper.txt

# 2. 检查原文中"先X后Y"的关键短语:
#    "SMOTE → after that → 80/20 split" = LEAKAGE
#    "split → then → SMOTE on training" = CORRECT
#    "global" + "SMOTE" + no mention of CV = LEAKAGE

# 3. 提取基线(unsampled)性能 vs 增强后性能
#    如果unsampled F1 ≈ 我方Helix F1 → 增强后膨胀=泄漏证据
```

### Step 4: 构建对照表

| 文献 | 报告指标 | 报告值 | 我方Helix值 | 膨胀幅度 | 原文证据 |
|:-----|:--------|:------|:-----------:|:--------:|:---------|
| Shams2025 | AUC | 0.99 | 0.451 (AdaBoost) | +120% | "up-sampling → after that, 80/20 split" |
| Li2024 | F1 | 0.9530 | 0.451 | +111% | 未采样基线F1=0.27 → +355% |

### Step 5: 论证链构建（论文集成）

```
三段论证结构:
  Claim: 文献中BRFSS高指标源于泄漏，非模型能力
    ↓
  Grounds: 
    └── Shams2025: 原文写"up-sampling→split"泄漏顺序
    └── Li2024: 同一论文基线F1=0.27→0.95(+355%)
    └── Tennessee2025: 唯一CV, F1=0.37↔我方0.45一致
    ↓
  Warrant: 泄漏模式∝不平衡度（+73.2% @13.8%, +11.1% @34.9%, -1.6% @61.5%）
    ↓
  Conclusion: 数据泄漏是系统性危机，非单数据集特例
```

### Step 6: 论文修改点

| 位置 | 内容 | 字数 |
|:-----|:-----|:----:|
| Abstract句尾 | 文献审计确认泄漏模式 | ~40词 |
| Related Work末段 | BRFSS文献逐文审计 | ~150词 |
| Discussion新增段 | 独立文献验证Helix thesis | ~130词 |
| References | +4篇BRFSS文献 | 4条 |

## 关键技术细节

### 全文验证文本模式（英语论文Methods节）

```text
# 🔴 LEAKAGE信号（红色警报）
"<sampling> was applied to <balance> the dataset. After that, 
 the data was split into X% training and Y% testing."

"Global SMOTE was used to address class imbalance before
 model training."

# ✅ CORRECT信号（绿色通过）
"SMOTE was applied exclusively within each cross-validation
 training fold, after the train-test split."

"To prevent data leakage, all preprocessing including SMOTE
 was encapsulated in the sklearn Pipeline within CV folds."
```

### openml Python模块使用（服务器可用时）

```python
import openml
# 列出数据集
dl = openml.datasets.list_datasets(output_format='dataframe')
# 筛选BRFSS
brfss = dl[dl['name'].str.contains('BRFSS|Health|CDC', na=False)]
# 获取基准任务
tasks = openml.tasks.list_tasks(data_id=brfss_did)
```

### Kaggle替代方案（当OpenML不可用时）

```bash
# Kaggle通过Tor可访问（需API key）
curl -s --socks5-hostname 127.0.0.1:9050 \
  "https://www.kaggle.com/api/v1/kernels/list?dataset=user/dataset"
```

## 关联skill

- `dual-quality-check-v2`: D6增强跨数据集验证协议
- `paper-pipeline`: P2论文构建（Related Work + Discussion）
- `research-paper-search`: 多源论文检索+PDF下载
- `pdf-download-racing`: Sci-Hub竞速下载
