# 撤稿论文审计 + 论文工厂模式检测

> 补充到 comprehensive-quality-report-template.md 的「报告生成流程」之后。
> 适用于用户要求检查某机构/作者的撤稿论文，或对已撤稿论文做质量审计。

## 第一步：机构/作者撤稿论文发现

### OpenAlex API 查询

```bash
# 按机构搜索撤稿论文
curl -s "https://api.openalex.org/works?filter=authorships.institutions.display_name.search:%22Wenzhou%20People%27s%20Hospital%22,is_retracted:true&per_page=50&sort=publication_year:desc"

# 按作者ID搜索撤稿论文（先查作者ID）
curl -s "https://api.openalex.org/authors?search=Yingying+Jiang&per_page=5"
curl -s "https://api.openalex.org/works?filter=authorships.author.id:A5042986217,is_retracted:true&per_page=20"
```

### ⚠️ 中文姓名消歧陷阱（关键教训）

**问题**：OpenAlex 对常见中文姓名（Yue Lin、Yingying Jiang、Wang Lv）的消歧极其糟糕。
- 一个 Author ID 可能对应几十到几百个同名但完全不同的研究者
- 以 Yue Lin (A5042064600) 为例：63篇论文分别来自北京、美国 NIH、日本等多国研究者
- 机构级过滤 `authorships.institutions.id:I4210152237` 仅匹配**论文级**机构，不匹配作者级机构
- 即使用户的论文中该作者的机构是"Wenzhou City People's Hospital"，OpenAlex 机构过滤也可能返回 0 结果

**可靠方法：Co-author 重叠交叉验证**

最可靠的鉴别方法不是靠机构名，而是：**同一机构中，多篇撤稿论文之间共同作者重叠**。

```python
# 方法：对每个候选作者，查所有论文 → 只看其中≥2位可疑作者合作的论文
target_ids = {'A5042064600','A5103667022','A5009931827','A5042986217','A5067441365','A5030819369','A5027765887'}
candidates = {}  # placeholder
for w in openalex_results:
    matched = [a for a in w.authorships if a.author.id in target_ids]
    if len(matched) >= 2:  # ≥2位可疑作者的论文 → 强信号
        candidates[w.doi] = w  # 确认是同一个研究组
```

实战验证：4位作者各自的OpenAlex结果各含几十至几百篇论文，但**只有3篇**有≥2位可疑作者共同署名，其中2篇已撤稿，1篇发现为新目标。

**搜索策略三管齐下：**

| 方法 | 可靠性 | 覆盖范围 |
|:-----|:------:|:---------|
| OpenAlex author ID → 逐篇检查机构（按DOI查） | 高（但慢，需逐篇） | 窄（仅已知ID） |
| **Co-author重叠过滤**（同一组人合作论文） | ⭐最高 | 中等（仅捕获合作论文） |
| CrossRef → 按DOI逐篇查 | 高（DOI精确） | 窄 |
| OpenAlex institution filter（I4210152237） | 低（遗漏作者级机构） | 宽但不准 |

**检索中文作者撤稿论文的推荐流程：**

1. 如果已知撤稿论文的DOI → 直接用Crossref/OpenAlex查该DOI → 提取作者列表
2. 对每个作者，用OpenAlex Author ID查全部论文（注意：名同人异）
3. 过滤条件：只看**该作者与已知撤稿作者中其他人共同署名的论文**（≥2人合作 = 强信号）
4. 对过滤出的论文，逐个检查撤稿状态（`is_retracted`）和期刊
5. 人工检查未被OpenAlex标记的潜在问题（使用下方论文工厂检测）

**不推荐**：直接搜"作者名 + 机构"的API查询，结果太嘈杂或太稀疏。

### 撤稿信息查询渠道（用户问题）

| 渠道 | 链接 | 覆盖 | 说明 |
|:-----|:-----|:-----|:------|
| **Retraction Watch DB** | retractiondatabase.org | ⭐ 最全 | 人工维护，可按作者/机构/期刊/年份搜索 |
| **PubMed** | pubmed.ncbi.nlm.nih.gov | 生物医学 | 检索 PMID 看是否标记 Retracted Publication |
| **Crossref** | api.crossref.org → `update-to` 字段 | 所有DOI | 每个DOI可查是否有 retraction notice |
| **OpenAlex** | `is_retracted:true` 字段 | 全学术 | 批量查询最方便，但中文名消歧不准 |
| **PubPeer** | pubpeer.com | 发表后评议 | 可看到撤稿通知全文和社区讨论 |
| **期刊官网** | 各期刊网站 | 正式来源 | 撤稿声明的权威来源，但常需CAPTCHA |
| **Semantic Scholar** | semanticscholar.org | 广 | 会标注 Retracted，可在API中查到 |

最有效路径：**Retraction Watch DB** + **OpenAlex**（已知作者ID时） + **Crossref逐篇验证**。

## 第二步：全文下载通道（针对已撤稿论文）

撤稿论文的 PDF 多数被出版商封锁，可用以下通道：

| 通道 | 适用场景 | 命令 |
|:-----|:---------|:-----|
| **MedData** | 机构订阅（温州市人民医院） | `download_one.py PMID:xxxxx /tmp/output.pdf` |
| **EuropePMC** | 有PMC ID的论文 | `https://europepmc.org/articles/PMC{PMID}?pdf=render` |
| **PubMed Central** | 有PMC的论文 | `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{PMID}/pdf/` |
| **Semantic Scholar** | OA论文 | `api.semanticscholar.org/graph/v1/paper/DOI:xxx?fields=openAccessPdf` |

⚠️ 撤稿论文在 ScienceDirect/Hindawi 上被封禁，不建议尝试 curl 直接下载。

MedData 调用方式（已验证对 Elsevier 撤稿论文有效）：
```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
python3 download_one.py PMID:38996709 /tmp/output.pdf
```

## 第三步：撤稿论文四报告QC

按 comprehensive-quality-report-template.md 标准四报告结构，但注意：

### 报告一（六域）评分调整
- 撤稿论文的 Q4（实验问）评分应反映撤稿调查发现的具体问题
- 撤稿通知中的问题直接映射到对应域扣分
- L0.5 数据铁律：如有 OpenAlex 标记 `is_retracted:true` 直接标记为 ❌ FAIL

### 报告二（专项）按论文类型
- 基础实验（斑马鱼/细胞）：评估样本量、统计方法、重复性
- 临床RCT：评估随机化、盲法、样本量计算、伦理审批
- miRNA/组学：评估多重比较校正、GEO提交

### 报告四（检查员）新增维度
- **Block 5：论文工厂模式检测**（见下方）

## 第四步：论文工厂模式检测

### 检测清单

| 指标 | 检测方法 | 权重 |
|:-----|:---------|:----:|
| **期刊-内容不匹配** | 论文主题是否在期刊scope范围内？心理学论文发表在计算数学期刊=🔴 | 高 |
| **跨领域作者** | 同一作者是否在完全无关的领域发表论文？（如生化+心理+整形） | 高 |
| **共同作者重叠** | 多篇撤稿论文之间是否存在稳定的共同作者群体 | 高 |
| **Hindawi/Wiley集中发表** | 论文是否集中在已知论文工厂重灾区期刊 | 中 |
| **通讯邮箱非机构** | 通讯作者用 outlook/gmail 等非机构邮箱 | 中 |
| **作者身份与课题无关** | 急诊科医生发表分子生物学论文 / 内镜中心发表心理学论文 | 中 |
| **数据不可获取** | 无GEO/无原始数据/无临床试验注册/无伦理审批号 | 中 |
| **统计方法明显缺陷** | 无多重比较校正 / 无效应量 / 无样本量计算 | 中 |
| **预注册缺失** | 临床试验无注册号（ChiCTR/ClinicalTrials.gov） | 低 |

### 作者重叠网络分析

```python
# 提取多篇撤稿论文的作者交集
papers = [
    {"doi": "10.1016/j.biopha.2024.117117", "authors": ["Yingying Jiang","Zheyan Chen","Yue Lin"]},
    {"doi": "10.1155/2022/7822847", "authors": ["Yue Lin","Yingying Jiang","Zheyan Chen"]},
    {"doi": "10.1155/2022/4085039", "authors": ["Jie Lin","Buyi Zheng"]},
]
# 计算作者重叠矩阵
```

### 综合判定

如果 >=3 项论文工厂指标命中，标记为：
- [WARN] **可疑** — 需进一步调查
- [CRIT] **高概率论文工厂** — 期刊-内容不匹配 + 跨领域作者 + 作者重叠三项同时命中

### ⚠️ 论文工厂 = 科研诚信不端（用户纠正 2026-06-25）

**论文工厂参与不是"出版流程问题"，是明确的科研诚信不端。** 依据：

| 依据 | 条款 |
|:-----|:------|
| COPE（国际出版伦理委员会） | 委托代写代发、推荐假审稿人 → 学术不端 |
| 科技部《科研诚信案件调查处理规则》 | 第三方代写代发 → 构成学术不端 |
| 国自然基金委《科研不端行为处理办法》 | 标注基金号的撤稿论文 → 追回项目经费 |
| 卫健委"九不准" | 买卖论文、代写代发 → 纪律处分 |

**质量报告语言必须对应升级：**
- ❌ 错误："这是出版流程问题，不是个人诚信问题，备案了事"
- ✅ 正确："论文工厂 = 科研诚信不端，属于 A 类+违规，须科研诚信事件备案"

**处理层级建议（基于国内三甲医院实际案例）：**

| 情节 | 处理 |
|:-----|:------|
| 1-2 篇 Hindawi 撤稿，无基金标注 | 诫勉谈话 + 退回论文绩效 + 诚信培训 |
| 3 篇+ 同模式撤稿，有基金标注 | 暂停硕导资格 + 取消职称申报 3 年 + 向基金委报告 |
| 数据造假+论文工厂双重违规 | 撤销学位（湘雅案例） |

### 撤稿论文大规模扫描：温州医科大学系统（2026-06-25 实战）

使用 OpenAlex 批量查询各机构的撤稿论文数（`is_retracted:true`）：

## 实战案例

### 温州市人民医院（2026-06-25）

| 论文 | 期刊 | 撤稿原因 | 指标命中 |
|:-----|:-----|:---------|:---------|
| BMRI 胶质瘤 miRNA | BioMed Res Int (Hindawi) | 批量撤稿 | 数据矛盾 |
| Biomed Pharmacother 斑马鱼 | Biomed Pharmacother (Elsevier) | 逐图审查/数据不可靠 | 统计数据问题 |
| Comput Math Methods Med CBT+EMDR | Comput Math Methods Med (Hindawi) | 批量撤稿 | **期刊-内容不匹配+跨领域作者+作者重叠** |

| 第3篇为典型论文工厂模式：临床心理学RCT发表在计算数学期刊，作者与斑马鱼论文完全重叠，内镜中心/整形外科的临床医生同时发表基础生化和心理学研究。

### 温州医科大学系统撤稿全景（扩展扫描）

| 机构 | OpenAlex ID | 撤稿论文数 |
|:-----|:-----------:|:----------:|
| **温州医科大学（主校区）** | I27781120 | **374** |
| 附属第一医院 | I2801769982 | 99 |
| 温州市人民医院 | I4210152237 | 8 |
| 温州中心医院 | I4210099759 | 19 |
| **合计** | | **>500** |

**通讯作者网络（温人医 8 篇撤稿）：**
- 陈泽燕团队（2篇撤稿 + 1篇可疑）：斑马鱼线粒体 / CBT心理学 / 纳米塑料铜死亡
- 郑卜毅团队（1篇撤稿 + 1篇高度可疑）：miR-339-5p 胶质瘤 ×2（同一基因在同一个Hindawi投了两篇）
- 张张（Zhang Zhang）（2篇全撤，100%撤稿率）：宫颈癌生物信息学，手机号邮箱 15088554408@163.com
- Dingdao Chen（1篇）：Contrast Media 围术期细胞因子
- Bang-Cheng Ma（1篇）：BMRI 脑肿瘤MRI分割
- Qian Zhuo（1篇）：无机化学配位聚合物（**跨领域 - 医院发配位化学，论文工厂信号**）
