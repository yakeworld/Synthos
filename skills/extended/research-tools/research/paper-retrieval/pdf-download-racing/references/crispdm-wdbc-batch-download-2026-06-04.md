# crispdm-wdbc 31篇引文批量下载记录 (2026-06-04)

> **目的**: crispdm-wdbc 论文参考文献PDF全覆盖，提升D9从22%→54%
> **方法**: Sci-Hub下载器 + Tor代理 + OA直连 + paper-manager后备

## 结果汇总

| 指标 | 值 |
|:-----|:---|
| 参考文献总数 | 31 |
| 原始PDF | 10 (32%) |
| 新增Sci-Hub | +8 |
| 新增Tor | +1 (Fernandez2018 SMOTE) |
| 新增arXiv | +1 (Wen2024) |
| 最终真实PDF | 17 (54%) |
| 仍缺 | 14篇（付费墙或Sci-Hub无）|

## 新增PDF清单（8篇）

| 引用 | 大小 | 下载源 | 出版社 |
|:-----|:----:|:-------|:-------|
| Collins2015 TRIPOD | 1.8MB | Sci-Hub .ru | Ann Intern Med |
| Moons2019 PROBAST | 228KB | Sci-Hub .red | Ann Intern Med |
| Mangasarian1995 WDBC | 532KB | Sci-Hub .red | INFORMS |
| Cruz2006 Breast | 144KB | Sci-Hub .vg | Cancer |
| Norgeot2020 MICLAIM | 770KB | Sci-Hub .red | Nat Med |
| Dietterich1998 Stats | 234KB | Sci-Hub .ru | Neural Computation |
| Hanley1982 AUC | 1.4MB | Sci-Hub .ru | Radiology |
| McDermott2021 Reproducibility | 258KB | Sci-Hub .ru | Patterns |
| Fernandez2018 SMOTE | 483KB | Tor→JAIR OA | JAIR |
| Wen2024 Leakage | 650KB | arXiv | arXiv |

## 仍缺的论文（14篇）

### Sci-Hub无（Springer/Elsevier 2022+）
- Feurer2025 OpenML (10.1007/s10994-024-06624-0) — Springer
- Alkhatib2023 (10.1007/s00521-022-07850-2) — Springer
- Araujo2023 (10.1007/s10916-017-0859-2) — Springer
- Elghazel2022 (10.1016/j.inffus.2022.01.015) — Elsevier
- Alkhasawneh2018 (10.1007/s11063-021-10578-y) — Springer
- Zhang2021 (10.1186/s12880-021-00621-8) — BMC (OA应可下)

### Sci-Hub无（其他出版社）
- Smith1988 PIDD (10.2337/diab.37.11.1545) — Diabetes
- Wolberg1995 WDBC (10.1007/978-1-4612-0719-9) — Springer book
- Ke2017 LightGBM (10.5555/3294771.3294774) — NeurIPS
- Kapoor2024 Leakage (10.1016/j.patter.2023.100804) — Cell Press

### 无正规DOI
- Street1993 WDBC — 会议论文
- Wirth2000 CRISPDM — 会议论文
- Janosi1988 Heart — 旧论文
- Dua2019 UCI — 网站

## 关键发现

### Sci-Hub状态
- `sci-hub.ru` ✅ 最稳定，下载8篇成功
- `sci-hub.ee` ✅ 备选
- `sci-hub.red` ✅ 部分成功
- `sci-hub.vg` ✅ 部分成功
- 2022年后Springer/Elsevier论文Sci-Hub覆盖不足

### Tor状态
- Tor运行中（端口9050，debian-tor PID 3178，已运行2周+）
- 通过Tor成功下载JAIR OA论文
- Cell Press/Springer直接拦截Tor节点

### MedData状态
- SSO type="0" 认证成功
- modifyPass=1标记阻断全文下载
- 需到medbooks.com.cn手动改密后方可全文访问

### DOI验证陷阱
- Kapoor2024 bib中DOI `10.1016/j.patter.2024.100974` 指向的是另一篇Kapoor论文（federated learning），非期望的Leakage论文（正确DOI: `10.1016/j.patter.2023.100804`）
- 下载前先用SS API验证DOI指向
