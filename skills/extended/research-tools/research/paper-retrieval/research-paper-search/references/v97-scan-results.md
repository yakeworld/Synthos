# v97 综合扫描结果（2026-06-08）

## 扫描摘要

第97轮综合扫描。5个旋转方向 + 10个候选验证 + 7个新高价值 + 6个深度PINN/ODE + 12个附加候选 + OpenAlex审计。

## 旋转方向结果

| 方向 | PubMed | 状态 |
|------|---------|------|
| VOR-PINN | 0 | ABSOLUTE WHITE |
| Kappa-ML | 27 | 全部无关（orthodontic angle, CBCT morphology, gastric filling ultrasound）→ FALSE POSITIVE |
| BPPV-nystagmus-ML | 8 | 3+直接ML临床 → 竞争稳定，NO PINN → PINN仍白 |
| PD-saccade-ML | 12 | 临床/综述 → 部分白稳定 |
| 3D-Eye-Tracking | 19 | 预期竞争（3DeepVOG框架, 疲劳+眼追踪, 放疗）→ NOT PINN/ODE |

## 候选验证（10个）

- 6/10 → ABSOLUTE WHITE: smooth-pursuit-PINN, VOR-cancellation-PINN, binaural-vestibular-ODE, vestibular-spinal-PINN, oculocardiac-reflex-ODE, concussion-oculomotor-PINN
- fixation-stability-PINN=40 → **假阳性**: metal oxides encapsulation (Small Methods), fracture reduction robot trajectory tracking → 经典fixation/stability关键词碰撞（与cancer cell fixation和network stability碰撞）
- oculomotor-NeuralODE=1 → 经典计算神经科学 → NOT NeuralODE → WHITE
- vestibular-paroxysmia-PINN=5 → LLM dizzy history, ML分类 → NO ODE/PINN
- VEMP-PINN=4 → ML临床预测模型, Meniere发作预测 → NO ODE/PINN

## 深度PINN/ODE（6/6）

全部ABSOLUTE WHITE: vestibular-computation-PINN, BPPV-canalith-ODE, caloric-nystagmus-PINN, head-impulse-ODE, vestibular-efferent-PINN, oculomotor-burst-NeuralODE

## 附加新候选（12/12）

全部ABSOLUTE WHITE PubMed=0: eye-head-coordination-PINN, pupillary-vestibular-PINN, vergence-accommodation-coupling-PINN, optokinetic-afternystagmus-ODE, velocity-storage-vestibular-PINN, fixation-vernier-PINN, dissociated-ocular-torsion-PINN, bifocal-fixation-PINN, saccade-target-shift-PINN, tonic-VOR-PINN, vergence-PINN, head-impulse-test-PINN

## 假阳性审计 — acoustic-vestibular-evoked-PINN=80

**重大假阳性发现**。80条PubMed命中，全部为：
- 原位听神经瘤小鼠模型（tumor-host interactions）
- 半规管顶裂有限元分析（finite element analysis）
- 其他肿瘤生物力学/工程论文

关键词碰撞：`acoustic` + `vestibular` + `evoked` + `response` + `model` → 命中肿瘤宿主相互作用和生物力学有限元分析，**完全不是PINN/ODE的听觉诱发响应建模**。

**分类决策**：COMPETITIVE count but FALSE POSITIVE。所有80条均不是计算动力学建模。PINN/ODE方法学在该查询下仍是ABSOLUTE WHITE。

## OpenAlex假阳性审计

| 查询 | 计数 | 假阳性模式 |
|------|------|-----------|
| cochlear-vestibular-PINN | 2 | NF1/NF2/schwannomatosis综述 → NOT PINN/ODE |
| fixation-PINN | 4969 | predictive brains, photothermal therapy, PET → classic PINN关键词碰撞 |
| smooth-pursuit-PINN | 37 | metamaterials, harbour porpoise, UAV → ALL FALSE POSITIVE |
| VOR-cancellation-ODE | 887 | saccadic targets, impulsivity, preoperative eval → FALSE POSITIVE |
| vestibular-spinal-ODE | 213 | verticality perception, concussion, rotation reflex → FALSE POSITIVE |

## 结论

170+ 白空间确认稳定。85篇论文完成，3个held。下一个候选：从12个ABSOLUTE WHITE候选中选择Paper 86（推荐：vergence-accommodation-coupling-PINN, score=20, convergence insufficiency 6%+ population, zero computational dynamics model）。
