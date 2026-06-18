# PubMed OR 假阳性 — 量级数据与阈值

## 现象

PubMed eSearch 的 OR 语义会匹配任一关键词出现在任何上下文中。当查询包含常见技术词（ODE, PINN, model, neural, learning, network, etc.）时，即使加上领域词，也会产生海量不相关结果。

## v20 扫描实例（2026-06-06）

| 精确查询 | PubMed 计数 | 相关性 |
|---------|-------------|--------|
| `concussion pupillometry machine learning` | 137,007 | 几乎全部无关（MRI, EEG, forensic, etc.）|
| `tinnitus computational model OR simulation` | 1,091,619 | 全部无关 |
| `tinnitus deep learning OR machine learning` | 261,163 | 全部无关 |
| `tinnitus physics-informed OR neural ODE` | 225 | 全部无关 |
| `saccade burst neuron ODE OR differential equation OR PINN` | 26,971 | 全部无关（生物/癌症/生化学）|
| `vestibular collic reflex ODE OR PINN OR neural ODE` | 881 | 全部无关（生物化学、色谱、肺动脉等）|
| `vestibular collic reflex PINN OR physics-informed OR ODE` | 802 | 临床前庭论文，无计算建模 |
| `endolymph hydropressure ODE` | 0 | **真实白空间** |
| `saccade burst neuron dynamics differential equation OR PINN OR NeuralODE` | 8 | 全部经典神经科学，零计算模型 |
| `tinnitus PINN OR neural ODE OR computational model` | 0 | **真实白空间** |

## 阈值规则

| PubMed 计数 | 判断 |
|-------------|------|
| > 500,000 | 几乎可断定假阳性（~39M 总论文库）|
| > 100,000 | 几乎可断定假阳性 |
| > 10,000 | 高度可疑，逐条检查前10条 |
| > 1,000 | 高度可疑，逐条检查前3条 |
| > 100 | 可疑，逐条检查前3条 |
| < 100 | 值得关注，但需验证相关性 |

## 修复策略

1. **使用 AND 组合**：`"endolymph hydropressure" AND model` — 比 `endolymph OR hydropressure OR model` 更可靠
2. **使用精确短语**（引号包裹）：`"vestibulo-ocular reflex" AND PINN AND model`
3. **避免纯 OR**：永远不要用 A OR B OR C OR D OR E — 每个词都会独立匹配
4. **计数 > 5000** → 几乎可断定假阳性，无需逐条检查
5. **交叉验证**：OpenAlex `cited_by_count:1-` 过滤作为第二层验证

## 常见触发词（高频假阳性源）

| 词 | 典型不相关领域 |
|----|---------------|
| ODE | 数学、物理、工程、金融 |
| model | 几乎所有领域 |
| neural | 生物、神经科学、材料 |
| learning | 几乎所有领域（reinforcement learning in logistics, etc.）|
| network | 社交网络、通信、电力、物流 |
| PINN | 物理、化学、流体力学 |
| deep learning | 几乎所有领域 |
| AI | 几乎所有领域 |
| 3D | 几乎所有领域 |
| 3D | 几乎所有领域 |
| saccade | 偶尔（生物学、心理学）|
| collic | 肠(colitis)、其他 |

## 验证流程

1. PubMed 搜索 → 记录 count
2. 如果 count > 1000 → 检查前 3 条标题
3. 如果前 3 条都不相关 → **视为 0 结果**
4. 对疑似白空间 → OpenAlex `cited_by_count:1-` 交叉验证
5. 对 OpenAlex 前 5 条 → 检查标题相关性
6. 用 3-4 种同义词变体搜索确认

## 关联

- `references/3-domain-gap-verification.md` — 3域验证协议
- `references/white-space-scan-2026-06-05.md` — OpenAlex 白空间扫描
- `references/api_quirks.md` — PubMed idlist 键名修复
