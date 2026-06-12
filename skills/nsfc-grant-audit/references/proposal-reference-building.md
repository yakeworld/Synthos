# 申报书参考文献建库工作流

> 2026-05-25实战验证：从6条→20条验证文献，D7评分从0.6→1.0
> 目标：20条可验证参考文献，覆盖6个方向，每条标注PMID或DOI

## 流程

### 第一步：NotebookLM联网检索（3-4个方向并行）

```bash
notebooklm source add-research "方向1: RFID/RTLS hospital asset tracking" --mode deep --no-wait
notebooklm source add-research "方向2: medical equipment lifecycle management" --mode deep --no-wait
notebooklm source add-research "方向3: healthcare IoT security" --mode deep --no-wait
notebooklm source add-research "方向4: Chinese hospital informatization RFID" --mode deep --no-wait
notebooklm research wait --import-all
```

### 第二步：Gemini推荐20条

```bash
notebooklm ask "基于笔记本中所有文献，推荐20条参考文献覆盖6个方向：1.RFID/RTLS医院资产管理 2.设备全生命周期管理 3.医院信息系统集成与业财融合 4.IoMT安全 5.中国公立医院资产管理 6.预测性维护。每条GB/T 7714-2015格式，标注PMID或DOI。必须基于真实可查文献。"
```

### 第三步：PubMed E-utilities逐条验证

```python
import requests, time

def verify_ref(title_terms, author, year):
    """Search PubMed with year±1 tolerance"""
    for y in [year, year-1, year+1]:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", 
                    "term": f"({title_terms}) AND {author}[Author] AND {y}[dp]",
                    "retmode": "json", "retmax": 3},
            timeout=10
        )
        data = r.json()
        count = int(data["esearchresult"]["count"])
        if count > 0:
            ids = data["esearchresult"]["idlist"]
            r2 = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
                timeout=10
            )
            detail = r2.json()
            for pid in ids:
                info = detail["result"][pid]
                print(f"✅ PMID {pid}: {info.get('title','?')[:60]} ({info.get('source','?')}, {info.get('pubdate','?')[:4]})")
            return True
        time.sleep(0.5)
    return False

# 对每条Gemini推荐的文献：verify_ref(title_terms, author_lastname, year)
# 验证通过 → 保留PMID入文献列表
# 未通过 → 删除该条
```

### 第四步：未通过的处理

- 年份±1都搜不到 → 标记为疑似编造，删除
- 找替代文献：用PubMed搜索相同主题词，找到真实文献替换

### 6个方向覆盖目标

| 方向 | 目标条数 | 关键检索词 |
|:-----|:--------:|:-----------|
| RFID/RTLS医院资产管理 | 8-10条 | RFID asset tracking healthcare, RTLS hospital |
| 设备全生命周期管理 | 3-4条 | medical equipment management, lifecycle, CMMS |
| 医院业财集成 | 2-3条 | ERP integration, business process, HL7 FHIR |
| IoMT安全 | 3-4条 | IoMT security, healthcare IoT privacy |
| 中国医院管理 | 2-3条 | Chinese hospital RFID, 中文期刊 |
| 预测性维护 | 2-3条 | predictive maintenance medical equipment |

### 文献格式示例（GB/T 7714-2015）

[1] Yoo S, Kim S, Kim E, et al. Real-time location system-based asset tracking in the healthcare field: lessons learned from a feasibility study[J]. BMC Medical Informatics and Decision Making, 2018, 18(1): 90. PMID: 30200938.

注：正文中引用采用"Author（Year）"格式，与参考文献列表编号对应。正文不出现[1][2]方括号引用。
