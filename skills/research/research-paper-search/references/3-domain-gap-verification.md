# 3-Domain PubMed Gap Verification Pattern

## When to use
当 cron 会话需要快速验证某个研究方向的竞争空间状态（白空间/弱竞争/直接竞争）时使用。比 OpenAlex 更可靠（不依赖引用计数）。

## Protocol

### 3 个 PubMed 查询域

每个研究方向查 3 个维度：

| 域 | 查询模板 | 目的 |
|---|---|---|
| A: 方法论 | `QUERY AND ("deep learning" OR "machine learning" OR "neural network" OR "neural ODE" OR "physics-informed")` | 看是否有 AI/ML 方法应用于该领域 |
| B: 理论/建模 | `QUERY AND ("mathematical model" OR "ordinary differential equation" OR "ODE" OR "computational model" OR "system identification")` | 看是否有数学/控制理论建模工作 |
| C: 传统方法 | `QUERY AND ("parameter estimation" OR "system identification" OR "Robinson model" OR "N4SID" OR "Kalman")` | 看传统方法的成熟度 |

### 执行

```bash
# 每个域独立查询
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=DOMAIN_QUERY&retmax=10&retmode=json" -o /tmp/vor_domain.json
python3 -c "
import json
with open('/tmp/vor_domain.json') as f:
    papers = json.load(f).get('esearchresult',{}).get('idlist',[])
print(f'{domain}: {len(papers)} PMIDs')
if papers:
    ids = ','.join(papers[:10])
    import urllib.request
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + ids + '&rettype=abstract&retmode=text'
    print(urllib.request.urlopen(url).read().decode())
"
```

### 判定规则

| 结果 | 判定 |
|---|---|
| 所有域 = 0 结果 | **绝对白空间** |
| 域A = 0, 域B/C 有结果 | **方法论白空间**（建模存在但无AI方法）→ 强竞争位点 |
| 域A 有结果但全部不相关 | **语义相关但方向不同** → 弱竞争 |
| 所有域都有相关结果 | **直接竞争空间** → 需差异化 |

### 示例（VOR-PINN-ODE, 2026-06-05）

| 域 | PMID count | 相关内容 | 判定 |
|---|---|---|---|
| A: VOR+DL | 10 |  concussion ML, 3D mouse eye tracking — 全不相关 | 无AI应用于VOR动力学 |
| B: VOR+ODE | 10 | 数学建模(ROBINSON, Ramat2019) + 临床实验 — 无ML | 传统建模成熟 |
| C: VOR+SystemID | 10 | 传统系统识别(MELS, HybELS) — 无神经网络 | 传统方法成熟 |

**结论**: 方法论白空间 — 传统建模/系统识别成熟, 但无人用PINN/NeuralODE学习VOR参数。**强竞争位点**。

### Cron 日志格式

```
|[Cron] <date> | action=3domain_gap_verify | domain_A=<count> | domain_B=<count> | domain_C=<count> | verdict=<WHITE/WEAKLY/COMPETITIVE> |
```
