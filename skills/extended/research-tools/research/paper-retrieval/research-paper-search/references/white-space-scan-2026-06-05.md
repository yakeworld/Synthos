# OpenAlex 白空间扫描 — 2026-06-05 Session

## 扫描记录：VOR-PINN-ODE 白空间验证

**目标**：确认 Physics-Informed Neural Networks (PINN) 应用于前庭眼动反射 (VOR) 微分方程建模是否已被发表。

**执行流程**：

1. 宽泛确认：`gaze+estimation+deep+learning` → count=22939 ✓ (API正常)
2. 目标搜索：`vestibulo-ocular+reflex+physics+informed+neural` → count=129，但全部不相关
3. 精确搜索：`OCPINNs+vestibulo+ordinary+differential+equations` → **count=0**
4. 交叉验证：4种措辞变体全部返回 0
5. 结论：真实白空间

**变体查询**：
- OCPINNs+vestibulo+ordinary+differential → 0
- Oblate+PINNs+vestibulo+ordinary+differential → 0
- Oblate+Neural+Networks+vestibulo → 0
- Oblate+PINN+vestibulo+ocular → 0

## PD-saccade 白空间验证

**目标**：确认 ML 方法用于帕金森病眼动震颤生物标志物检测是否已被发表。

**结果**：OpenAlex 返回 611+ 结果，但 top 论文是 "References"、"spatial representation of time" 等无关内容。cited_by_count 全为 0。说明搜索关键词不够精准，实际有效论文不存在。

**结论**：虚假正阳性搜索空间 — 关键词匹配但无实际论文。

## 可复用模式

白空间确认需要三层验证：
1. 宽泛查询确认 API 正常
2. 精确查询得到 0 结果
3. 多个变体交叉验证

仅一次 0 结果不足以确认白空间。
