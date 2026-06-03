# 文献汇聚证据工作流 — Discussion独立验证

> 当跨数据集实验已证明泄漏效应（F1膨胀∝不平衡度），但审稿人仍可能质疑"这只是你们自己实验里的发现"时，通过文献审计提供独立验证。

## 触发条件

| 信号 | 行动 |
|:-----|:------|
| D6 Novelty < 0.80 | 跨数据集验证不够，需要文献证据加固 |
| Discussion论点需要"独立验证"句 | 文献全文定位泄漏→写入"文献也印证此模式" |
| 审稿人可能质疑"仅你系统内有效" | 外部文献确认是阻断此类质疑的最有力回应 |

## 三阶工作流

### 第一阶段：目标文献定位

```python
# 1. 找使用同一数据集的文献
# 用OpenAlex搜索（不限速，串行+2s间隔）
curl -s "https://api.openalex.org/works?search=BRFSS+diabetes+predict&per-page=25"

# 2. 筛选标准：
#   - 使用相同/类似数据集（同CDC BRFSS）
#   - 报告了具体性能指标（accuracy/AUC/F1）
#   - 方法部分可访问（OA论文优先）
#   - 时间范围：2020年后
```

### 第二阶段：全文方法学审计

**目标是定位原文中的确切泄漏语句和提取基线性能。**

#### 2A: 下载OA PDF

论文来源优先级：
1. **PLOS ONE / MDPI / SpringerOpen / Frontiers** — 固有OA，直连下载
2. **Hindawi / Wiley OA** — 虽然OA但被Cloudflare保护，用curl_cffi绕过
3. **arXiv** — 如有arXiv版本，arXiv PDF最稳定
4. **Sci-Hub** — 最后手段，2026年后新论文覆盖率低

下载后立即验证：`file paper.pdf` → `%PDF-` 头检查。

#### 2B: 精准定位泄漏语句

全文阅读目标：**找到数据预处理和train-test split的顺序描述。**

| 原文信号 | 泄漏判定 |
|:---------|:---------|
| "Up-sampling was applied to balance the data. **After that**, 80% were used as training..." | 🔴 **明确泄漏** — 全局采样→后分割 |
| "SMOTE was performed on the entire dataset before splitting" | 🔴 **明确泄漏** |
| "Data were preprocessed using SMOTE and then divided into training and test sets" | 🔴 **明确泄漏** |
| "After feature selection, we applied 10-fold CV" | 🔴 **全局特征选择→CV** |
| "Random oversampling + GridSearchCV" | 🟡 **可能泄漏** — 需确认采样是否在CV外 |
| "Stratified k-fold CV was used with SMOTE applied within each fold" | ✅ **正确隔离** |
| "Data augmentation was applied only to the training set" | ✅ **正确隔离** |

**提取原文段落和行号**，记录在审计笔记中。这是Discussion中最可信的证据——审稿人无法反驳。

#### 2C: 提取基线性能

最关键的证据不是报告的最好性能，而是**同一论文中未采样的基线性能**：

```python
# 搜索模式：寻找"without sampling"、"no processing"、"raw data"等基线
# 典型语句: "Without any sampling, the XGBoost model achieved F1=0.2682"
#              "After SMOTEENN, the F1 improved to 0.9530"

# 记录三组数值：
# 1. 未采样基线（可信性能）→ 与Helix结果对比
# 2. SMOTE/采样后性能（泄漏值）→ 与Leaky结果对比
# 3. 泄漏膨胀幅度 → 与实验Λ对比
```

**关键是**：正确的未采样基线应当与Helix结果在同一量级。如果SMOTE后性能暴涨（如F1 0.27→0.95），而同一论文无基线控制→这是泄漏的间接但强大的证据。

### 第三阶段：论文集成

#### 输出论证结构

```
Claim: 泄漏是系统性危机，非单数据集特例
  ↓
Grounds (来自本实验):
  - 我方跨数据集实验: 患病率13.8%→+73.2%, 34.9%→+11.1%, 61.5%→-1.6%
  - Helix协议 vs Leaky协议对比
  ↓
Warrant: 如果泄漏只发生在我的实验里，文献应该报告正确的低性能
  ↓
Grounds (来自文献审计):
  - Shams2025: 原文"up-sampling→split", AUC=0.99
  - Li2024: 未采样基线F1=0.27 vs SMOTEENN后F1=0.95
  - Tennessee2025: 唯一正确CV, F1=0.37 ← 与Helix一致
  ↓
Conclusion: 实验证据+文献独立验证→汇聚证据
```

#### Discussion段落模板

```latex
\textbf{Independent literature confirmation of the Helix thesis:} 
The published BRFSS diabetes literature independently validates our cross-dataset findings. 
Full-text audits of key studies confirm that their reported performance aligns with our 
Leaky protocol, not our Helix protocol. 
Shams \cite{Shams2025} reports AUC=0.99 on BRFSS using up-sampling applied before 
train-test split---the specific sequence we identify as the ``Severe Leakage'' condition, 
which produces F1 inflation of +73.2\%. 
Li et al. \cite{Li2024} report XGBoost+SMOTEENN achieving F1=0.95, yet their own 
unsampled baseline (F1=0.27) is nearly identical to our Helix-isolated AdaBoost 
result (F1=0.451). 
The only study employing proper stratified cross-validation on BRFSS, a Tennessee 
subpopulation analysis \cite{Tennessee2025}, reports a Gradient Boosting F1 of 
0.37---within the range expected under the Helix protocol. 
This cross-literature consistency demonstrates that the inflation pattern we measure 
experimentally is directly mirrored in the published literature: studies with proper CV 
report F1$\approx$0.37--0.45, while studies with global preprocessing report 
AUC$>$0.98.
```

#### 参数化模板（可复用）

| 变量 | 替换示例 |
|:-----|:---------|
| {Dataset} | CDC BRFSS, PIDD, MIMIC-IV |
| {OurMetric} | Helix F1=0.451 |
| {LeakyMetric} | Leaky F1=0.768 (+73.2%) |
| {LitReport1} | Shams2025: AUC=0.99 |
| {LitReport1Flaw} | "up-sampling before split"（原文p.3） |
| {LitReport2} | Li2024: F1=0.95 (SMOTEENN) |
| {LitReport2Baseline} | 未采样F1=0.27 |
| {LitControl} | Tennessee2025: F1=0.37 (stratified 5-fold CV) |

## 数据源

当直接下载不可行时，OpenML提供同一数据集的基准测试结果：
- `https://www.openml.org/d/{DID}` — 数据集详情页（含任务列表）
- `https://www.openml.org/t/{TID}` — 具体任务页（含算法排行榜）
- API: `https://www.openml.org/api/v1/json/task/list?data_id={DID}`

注意：OpenML上的benchmark结果本身可能有泄漏，需结合方法学审计判断。

## 陷阱

1. **泄漏论文也可能用CV** — Banchhor2021报告10-fold CV但特征选择在CV前，仍是泄漏。不能仅因"提到了CV"就判定方法可靠。
2. **Accuracy在不平衡数据上误导** — 患病率13.6%的CDC BRFSS全判非糖尿病即达86.4%。arXiv和Journal论文常只报Accuracy不报F1/AUC → 直接标记为方法不完整。
3. **未采样基线是关键** — 同一论文中unsampled基线F1=0.27 vs SMOTEENN后F1=0.95比任何外部基准都更能说明问题。
4. **不要只信摘要** — Shams2025摘要看不出泄漏，需读Methods找"up-sampling→split"顺序。
5. **不要过度声称** — "文献发现与我们一致"不同于"文献证实了我们的框架"。前者是汇聚证据，后者需要我们自己证明框架的因果作用。
