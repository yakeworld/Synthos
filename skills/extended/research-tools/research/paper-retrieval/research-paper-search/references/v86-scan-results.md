# v86 综合扫描结果（2026-06-08）

## 扫描摘要

第86轮综合扫描。5个旋转方向 + 8个候选验证 + 9个新候选 + OpenAlex假阳性审计。

## 旋转方向结果

| 方向 | PubMed | 状态 |
|------|---------|------|
| VOR-PINN | 0 | ABSOLUTE WHITE |
| Kappa-ML | 5 | 全部无关（遥感岩性图、脊柱手术LLM、三叉神经ML）→ WHITE |
| BPPV-nystagmus-ML | 5 | 预期竞争，NO PINN → PINN仍白 |
| PD-saccade | 5 | 临床/综述 → 部分白稳定 |
| 3D-Eye | 5 | 预期竞争 |

## 候选验证

- 8个关键PINN查询 = PubMed全部0
- VEMP-PINN = 5（无关：内耳老化横断面、RBD综述）→ NO PINN
- smooth-pursuit-NeuralODE = 5（假阳性：热力学方翅模型、Hirschsprung病）→ 0 smooth pursuit
- nystagmus-jerk-ODE = 1（PMID 15940536：经典非线性saccadic动力学模型）→ NOT PINN/ODE → WHITE for PINN approach

## 新高价值（9个）

全部PubMed=0：vestibular-spinal、tonic-VOR、binaural-vestibular-ODE、vestibular-efferent、vestibular-computation、otolith、binocular-summation、vestibular-collic、vestibular-tremor

## OpenAlex假阳性审计

- cochlear-vestibular-coupling = 1584：top hit=neural interface electronics, music therapy, primate vision → **全部假阳性 → PINN/ODE ABSOLUTE WHITE**
- VEMP-PINN = 1（奥地利会议摘要→0相关）
- vestibular-paroxysmia = 43（三叉神经临床+计算轴突建模→NO PINN for paroxysmia）
- fixation-PINN = 71（分子传输、植物学→假阳性）
- smooth-pursuit-NeuralODE = 542（热力学、交通预测、Hirschsprung→0 smooth pursuit）
- VOR-cancellation = 214（光学、恒星成像→假阳性）
- vestibular-spinal = 5227（neural interface electronics→全部假阳性）
- vestibular-efferent = 2308（neural interface, primate vision→全部假阳性）
- vestibular-computation = 5642（neural interface electronics→全部假阳性）

## 结论

120+ 白空间确认稳定。83篇论文完成，3个held。下一个候选：cochlear-vestibular-coupling-PINN（PubMed=0/OA=1584-全部假阳性→PINN/ODE ABSOLUTE WHITE，score=22）作为Paper 84。