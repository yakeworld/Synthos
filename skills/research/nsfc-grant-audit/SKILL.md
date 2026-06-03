---
name: nsfc-grant-audit
description: "主skill | 中国科研课题评审编排器。覆盖NSFC/省科技厅/市科技局三级。九维评审矩阵+重建型/评审型双路径工作流。调用子skill: research-paper-search, pubmed, notebooklm-cli"
signature: "input: dict -> output: dict"
related_skills: [academic-paper-completion, adhd-eye-tracking-review, arxiv, biorxiv, blogwatcher]
allowed-tools: [terminal, read_file, write_file, search_files]
version: 2.6.0
author: Synthos
license: MIT
metadata:
  hermes:
    tags: [grant, nsfc, proposal, review, orchestrator]
    related_skills: [research-paper-search, pubmed, notebooklm-cli, paper-pipeline]
---

# NSFC Grant Audit — 课题评审编排器

## 核心原理（文言）

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 经费来源决定一切 | **资源定器** | 面上≈50万/青年≈30万/省厅10-30万/市局1-5万，预算直接决定设计可行性 |
| 工具必须匹配声称指标 | **器必称言** | 说"评估认知"必须用捕捉认知的工具，不止量表 |
| 参考文献必须可验证 | **引必可证** | 中文申报书英文引用常编造，抽查≥50%英文引用 |
| 数据源需查公开资源 | **源必稽库** | 涉及影像+ML的标书，需查是否有公开数据集可补充/验证方案 |

## 触发条件

自动：用户上传含"可行性分析报告/申报书/标书/任务书"文件，或提及"NSFC/市科技局/省基金/面上/青年"。
手动：用户说"评审/评估/审查标书/申报书"、"写评审意见"、"修改/优化申请书"。

## ⚡ 重建型 vs 评审型 — 双路径选择

**这是本skill的入口判定。用户给了一份标书后，先判定场景，再执行对应流程。**

> **2026-05-25 实战教训**：用户给了一个RFID项目草稿说"优化"，我直接按评审型处理（P1→P3→P4），跳过了文献发现环节，导致方案零引用、硬件选型与指标矛盾。用户纠正后才回到正确的P0流程。**先P0再做P1是铁律。**

**🚨 常见错误场景及其正确做法**：

| 用户说 | 易犯错误 | 正确做法 |
|:-------|:---------|:---------|
| "帮我优化这个申报书" | 打开文档直接修改 | 先走P0文献发现→Gap→假设→再打开文档 |
| "评估这个标书质量" | 直接给九维评分 | 先走P0检查是否有文献支撑，无引用则降级处理 |
| "帮我写一份申请" | 直接套模板填内容 | 先走P0做文献检索，Gap定位决定方向再动笔 |

| 场景 | 触发条件 | 起点 | 流程 |
|:-----|:---------|:-----|:-----|
| **A. 评审型**（标书已完备） | 用户上传完整标书要求评估 | P1 文档解析 → P2 验证 → P3 评分 → P4 修正 | 原九维评审矩阵 |
| **B. 重建型**（草稿/模板） | 用户给了一份草稿或重复套话模板，要求"优化" | **先走P0文献发现 → 再走P1-P5** | 新增流程 |

**🚨 常见错误**：用户给了一份草稿或模板，要求"优化"。直接跳到P1解析和P3评分，会跳过文献发现环节，导致：
- 方案没有文献支撑 → 标书被批"零引用"
- 技术路线沿用草稿的落后方案 → 创新性不足
- 研究内容与真实空白不匹配 → 逻辑断裂

> **铁律：先P0再做P1。** 草稿只是起点，不是终点。在触摸标书文件之前，先做文献检索→空白发现→假设形成。

---

## 工作流地图

| 阶段 | 做什么 | 加载哪个子skill |
|:-----|:-------|:---------------|
| **P0 文献发现** | **先不看标书。** 新建NotebookLM项目→联网检索文献→逐问法发现Gap→形成可证伪假设 | paper-pipeline (P-1流程); notebooklm-cli; references/notebooklm-proposal-optimization.md |
| P1 文档解析 | 读标书全文，判断经费级别 | — |
| P2 文献验证+数据源检查 | 抽查英文参考文献真实性；如涉及影像+ML，查公开数据集 | research-paper-search; references/public-medical-datasets.md |
| P3 九维评审 | 逐维评分+写具体意见，校准到经费级别 | — |
| P4 重构方案 | 修正缺陷后输出完整标书；含技术路线图生成 | paper-pipeline; references/proposal-diagram-generation.md; creative/academic-diagram |

**P4 格式铁律**：输出必须严格对标原始模板的章节格式（七节体系），**不得重塑为Synthos的认知原子格式**。Synthos理念通过内容嵌入（H₃假设、L0.5声明、门控节点、文献引用、参考文献列表），不是通过改变章节目录。

2026-05-25实战教训：将申报书改写为空白→假设→原子分解→门控格式后，用户纠正——输出被否决，不得不重写回原格式。

**常见格式合规检查清单**：
- [ ] 标题行保留"温州市科技项目可行性分析报告"（不可改）
- [ ] 七节编号正确：一、~七、，中间无缺失
- [ ] 子节编号正确：（1）（2）（3），无跳跃
- [ ] 指标表保留原表格式（左列指标名 + 右列数值）
- [ ] 进度安排按5个阶段写，每个阶段有交付成果
- [ ] 参考文献置于文末，不插入节内
|
| P5 闭环归档 | 上传到NotebookLM | notebooklm-cli |
| **P6 NotebookLM优化** | 上传申报书→联网补充文献→Gemini专家评审→整合输出 | nsfc-grant-audit; references/notebooklm-proposal-optimization.md |
| **P6.5 双质量检查** | L0.5门→Layer A→Layer B→校准分判定→修订循环（适配版，非SCI论文） | nsfc-grant-audit; references/proposal-dual-quality-check.md |

---

### P0 文献发现流程（重建型专属）

**铁律：在触摸标书文件之前，先做文献检索→空白发现→假设形成。** 这是从 paper-pipeline 的 P-1 阶段借鉴的 Synthos 标准流程。

```bash
# Step 1: 创建NotebookLM项目做文献底座
notebooklm create "项目名_文献底座"
notebooklm use <id>

# Step 2: 批量检索（3-4个并行deep research）
notebooklm source add-research "核心技术+application" --mode deep --no-wait
notebooklm source add-research "行业案例+cases" --mode deep --no-wait
notebooklm source add-research "中文文献+政策" --mode deep --no-wait
notebooklm source add-research "补充方向" --mode deep --no-wait

# Step 3: 逐问法探索（Q1→Q2→Q3→Q4）
notebooklm ask "**Q1 领域地图**: 这个领域最相关的工作是什么？主流技术方案的原理和局限？"
notebooklm ask "**Q2 共同盲区**: 这些方案共同的盲区？什么维度一直没人碰？为什么？"
notebooklm ask "**Q3 形式化Gap**: (1)已知 (2)未知 (3)填补价值"
notebooklm ask "**Q4 可证伪假设**: H₁主假设+H₂替代+淘汰标准"

# Step 4: 预算校准 — 用假设匹配经费级别
# H₁-高精度定位 → 需要硬件预算（≥5万，不适合市局）
# H₂-流程再造 → 需要组织行为学（≥12个月，时间不够）
# H₃-纯软件API方案 → 1-5万+12个月可完成，最适合市局
```

**产出**：一个明确的科学假设 + 可证伪条件 + 验证方法。然后才打开标书模板，用假设驱动内容重构。

**关键校验**：如果在P0阶段发现文献中已有N篇论文解决了类似问题 → 要么弱化创新为"工程验证"，要么找到尚未被覆盖的维度重新定位Gap。

---

### P6 NotebookLM优化流程（评审型补充流程）

当标书已基本写成、需要质量提升时，新建专用Notebook并上传：

```bash
# Step 1: 新建专用Notebook
notebooklm create "项目名_NotebookLM优化"
notebooklm use <id>

# Step 2: 上传标书全文（note create降级处理）
notebooklm note create "$(cat proposal.txt)" --title "申报书原文"

# Step 3: 联网补充相关文献（3个方向并行）
notebooklm source add-research "核心技术方向" --mode deep --no-wait
notebooklm source add-research "预算级别相关的案例" --mode deep --no-wait
notebooklm source add-research "政策/行业趋势" --mode deep --no-wait

# Step 4: 待研究完成后导入
notebooklm research wait --import-all

# Step 5: Gemini专家评审
notebooklm ask "请阅读笔记本中所有内容，从以下角度给出具体的优化建议..."

# Step 6: 提取优化建议整合进标书
```

**陷阱1**：NotebookLM note create 上传的内容可能被索引但搜索不到。CLI的 `source add --type file` 上传失败时，`note create` 是可靠的降级方案，但需要等数分钟才被Gemini检索到。若等不到，直接将核心信息写在ask的问题中替代。

**陷阱2**：UHF RFID 声称"定位准确率≥99%"是常见误区——UHF RFID是门禁级盘点技术，不是空间定位技术。如果预算只有1-5万，应诚实标注"区域级门禁盘点（≥95%可信区间）"，核心创新放在API数据同步而非物理定位。2026-05-25实战：Gemini Layer B审查准确发现了此矛盾。

### P3.5 参考文献建库工作流（P2-P3间执行）

当标书原始参考文献不足10条或无法验证时，在执行P2文献验证后、P3评分前，执行此工作流构建20条可验证参考文献：

```bash
# Step 1: NotebookLM联网检索（3-4个方向）
notebooklm source add-research "方向1关键词" --mode deep --no-wait
notebooklm source add-research "方向2关键词" --mode deep --no-wait
notebooklm source add-research "方向3关键词" --mode deep --no-wait
notebooklm research wait --import-all  # 导入结果

# Step 2: 让NotebookLM推荐20条参考文献覆盖6个方向
notebooklm ask "请基于笔记本中已有文献，推荐20条覆盖6个方向的参考文献，格式GB/T 7714-2015"

# Step 3: 用PubMed E-utilities验证每一条（含年份±1容错）
# 对每篇论文：作者+标题词+年份, 年份±1
python3 << 'EOF'
import requests, time
def verify(title_terms, author, year):
    for y in [year, year-1, year+1]:
        r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": f"({title_terms}) AND {author}[Author] AND {y}[dp]",
                    "retmode": "json", "retmax": 3}, timeout=10)
        data = r.json()
        if int(data["esearchresult"]["count"]) > 0:
            ids = data["esearchresult"]["idlist"]
            r2 = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"}, timeout=10)
            detail = r2.json()
            for pid in ids:
                info = detail["result"][pid]
                print(f"PMID {pid}: {info['title'][:60]} ({info['source']})")
            return True
        time.sleep(0.5)
    return False
EOF

# Step 4: 未通过验证的 → 删除；通过的 → 按年份排序编入参考文献列表
# Step 5: 每条文献标注PMID或DOI，确保评审专家可溯源
```

**目标**：20条参考文献，覆盖6个方向（RFID/RTLS、全生命周期管理、业财集成、IoMT安全、中文背景、预测性维护），每条标注PMID或DOI。2026-05-25实战验证：20条文献全部通过PubMed验证，D7评分从0.6提升至1.0（满分）。

---

## 九维评审矩阵

⚠️ **校准规则（P1必备）**：评分前先判断经费级别（面上≈50万/青年≈30万/省厅10-30万/市局1-5万）。同一标书在不同级别下评分不同——用A级标准评C级项目=不合理的严苛。各维度的级别依赖评分详见 `references/grant-review-dimensions.md`。

常见误判模式（用户多次纠正，2026-05-21更新）：
- ❌ 认为市局项目"论文1篇不够" → 1篇核心期刊对市局3年期是合理预期
- ❌ 认为需要升级产出目标 → 市局项目"1篇论文+临床工具"=完整结题
- ❌ 要求多中心外部验证 → 市局预算一般不支撑，Bootstrap 1000次内部验证即可
- ❌ 用NSFC创新标准评市局项目 → 市局接受"工程创新"（已知方法用于新疾病）
- ❌ 未查年份±1就判参考文献伪造 → 见 reference-verification pitfall

新增陷阱（2026-05-21 PD项目实操发现）：
- 🔴 **"首次"宣称审查（P1）**：创新点部分常见的"首次将...引入"宣称是靶子——审稿人/评审专家很难验证是否能称"首次"。应弱化为"系统地将...构建"或直接删除"首次"，用实质内容说话。检查模式：`首次[^。]{0,20}(?:提出|引入|构建|定义|建立)`
- 🔴 **样本量估算缺失（P2）**：部分标书只说"计划纳入N例"但不给出效应量→power→样本量的计算过程。正确写法应包含：预期效应量/参照文献、α、power、EPV(事件数/变量数≥10)、预期损耗率。检查文本中是否包含"样本量估算"或"Power分析"关键词。
- 🔴 **编写说明违禁检查（P0）**：温州市科技局可行性报告明确要求"不能出现项目申报单位和项目负责人、成员相关的信息"。检查以下敏感模式：
  - **高危（直接暴露）**："温州医科大学""INSTITUTION_NAME_PLACEHOLDER""温州市XXX医院"等完整机构名 → 必须删除或替换为"某医科大学""某医院"
  - **中危（暗示层级）**："温州市重点学科""温州市儿童生长发育中心""温州市高危儿干预中心""浙江省XXX基地" → 模糊化为"市级重点学科""省级示范基地"
  - **低危（模糊可审）**："依托单位""我院""我科""课题组" → 逐段审查，能删除则删除
  - **隐蔽模式**："温州市"前缀出现在学科/中心/基地名称中，即使未直接写医院名，也暗示了所属地区层级。应全部模糊化为"市级"
- 🔴 **知识产权"0项"陷阱**：申请人在预期目标中写"软件著作权0项""发明专利0项"，通常不是目标为0而是忘记填写。应提示补填：软件著作权≥1项、发明专利0-1项
- 🟡 **重复引用检测**：标书参考文献列表中可能同一篇文献被引两次（不同编号），如[11]=[15]是同一篇Rabab R 2023。按DOI去重对比可检出
- 🟡 **编号跳跃检查**：研究方案章节可能出现①→②→④→⑤→⑥，缺失③。这是复制粘贴后未更新编号的痕迹

---

## 参考文件

- references/grant-review-dimensions.md — 九维评分细则
- references/measurement-tool-adequacy.md — 工具充分性检查方法
- references/nsfc-budget-templates.md — 各级预算模板
- references/chinese-municipal-proposal-reconstruction.md — 市科技局标书重构全流程（含值类型年份勘误、跨Run文本替换陷阱、产出校准、公开数据集扫描）
- references/proposal-diagram-generation.md — 技术路线图生成与插入docx（TikZ模板位于templates/proposal-technical-roadmap.tex）
- references/public-medical-datasets.md — 公开医学影像数据集检索策略与已知资源
- references/literature-gap-analysis.md — 文献空白分析方法
- references/reference-formatting-guide.md — GB/T 7714-2015格式
- references/rebuild-proposal-from-notebooklm.md — NotebookLM重构
- references/oa-pdf-download.md — 开放获取PDF下载
- references/notebooklm-review-workflow.md — NotebookLM集成
- references/zero-cost-bedside-measures.md — 床旁测量工具
- references/notebooklm-proposal-optimization.md — NotebookLM标书优化工作流（含格式铁律）
- references/proposal-dual-quality-check.md — 申报书双质量检查协议（L0.5+7维适配版）
- references/proposal-reference-building.md — 20条可验证参考文献建库工作流
- references/paper-pipeline-p1-grant-adaptation.md — 论文管线适配申报书
