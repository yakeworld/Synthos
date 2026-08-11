# Synthos 问题跟踪 (PROBLEMS.md)

更新时间: 2026-08-12 (战略回顾 cron)

## 已解决 (Resolved)

| 编号 | 问题 | 解决日期 | 备注 |
|------|------|----------|------|
| P001 | BPPV 论文 submission 材料 | 2026-08-04 | 14项材料全齐 (highlights/graphical/credit/cover-letter) |
| P003 | 文献监控通道不可用 | 2026-08-05 | SearXNG + Tor 代理已配置 |
| P004 | 2026指南同行评审 | 2026-08-05 | 19条意见+21表已归档 (peer-review-report) |
| P005 | 3diris-01 论文缺图 | 2026-08-07 | fig:pca/fig:dilation 已补插, 0 undefined refs |
| P006 | 3diris-01/04 PDF 缺失 | 2026-08-07 | 已编译: 01=5页/393KB, 04=8页/409KB, 同步02-submission |
| P007 | train_shape_net 空转误报 | 2026-08-07 | 无真实进程, 系残留显存; BPPV视频5/5可达(NFS) |
| P008 | evolution-state.json 误报丢失 | 2026-08-07 | 实际存在: Cycle 210, score 0.9676, healthy |
| P009 | BPPV 仿真视频断链 | 2026-08-07 | 符号链接指向 /mnt/nfs/article/psc/ 源文件全部完好 (248MB) |
| P016 | 3diris-01 G10c state 未更新 | 2026-08-12 | G10c COMPLETE 已回写 (PCA r=0.0176 REJECTED / Pose r=0.9937 SOLVED), G系列收官 |
| P017 | 3diris-02/03 ghost paper 无 state.json | 2026-08-12 | 已回填 state.json, 02 建议合并/03 建议推迟 (COLMAP SfM 待评估) |

## 待解决 (Open)

| 编号 | 问题 | 严重度 | 状态 |
|------|------|--------|------|
| P010 | BPPV 论文 03-code/ 空目录 — 仿真代码缺失 | 🔴 P0 | 投稿阻塞项; 需从来源恢复或补写可复现脚本 |
| P011 | BPPV 论文正式投稿 (Elsevier EES 手动上传) | 🔴 P0 | 14项材料齐, 待人工操作 |
| P012 | state.json 管线 239/241 篇 phase=unknown | 🟡 P1 | 47天停滞, 需批量重扫描 |
| P013 | 28 篇 harvest 论文 NOT_STARTED 无评分 | 🟡 P1 | 参考论文(非产出), 可按需 quality-gate |
| P014 | 省级人才申报通道确认 | 🟡 P1 | 领军/青年/医坛新秀 待选 |
| P015 | 根分区 79% (62G 剩余) | 🟢 P2 | 持续增长需监控 |
| P018 | mmu-pd 数据解析执行中 | 🟡 P1 | proc_449ef47b8f86, 292 JSON→npz, 完成后接 H04 基线复现 |
| P019 | bbbd exp1 第三次下载中 (S3 131MB/893MB) | 🟡 P1 | 前两次 Zenodo+S3 混合分段损坏; 完成后 zip 完整性门禁+解压 |

## 误报澄清 (2026-08-07 简报)

- train_shape_net "空转" → 无真实进程, GPU 空闲正常
- evolution-state.json "丢失" → 实际存在 (Cycle 210, 0.9676)
- 文献监控 "无输出" → 今日 11 个 cron 输出正常
- Cron "last_run=never" → 22 任务全部 enabled 且正常产出
