# Synthos 问题跟踪 (PROBLEMS.md)

更新时间: 2026-08-13 (hourly-briefing in-run: P022, P023)

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
| P019 | bbbd exp1 第三次下载 (S3 混合分段损坏) | 2026-08-12 | 单源 S3 重下完成: 893MB testzip 3690文件 OK, 已解压 1.9GB BIDS (27被试), state.json 回写 data_ready_extracted |
| P018 | mmu-pd 数据解析执行中 | 2026-08-12 | 292 JSON→npz 解析完成, H04 基线复现 PASS (AUC 0.814 vs 原 0.87, 视频级CV); H01 时域变异 COMPLETE (AUC 0.622 PARTIAL, motion_cv p=2.9e-4); H02 关节指纹 COMPLETE (23:1x in-run: 髋/膝垂直振荡 PD↑ d=+0.31/+0.27 p<0.005, 右膝角CV↓ d=-0.39 p=0.03 强直表型, 关节LR AUC=0.649 PARTIAL); H03 相空间 COMPLETE (08-13 02:0x in-run: SampEn/Higuchi/LLE/关联维数 全不显著 |d|≤0.181 p≥0.099, AUC=0.566 REJECT, H04+H03=0.866 无增量 → 阴性对照入论文) — mmu-pd H 系列收官 |
| P020 | bbbd H02 相空间重构 (连续3简报空转) | 2026-08-12 | 16:15 in-run 执行 COMPLETE: sampen_pupil 分心↓ (d=-0.89, p=6e-4) + hfd_gazespeed 分心↓ (d=-1.10, p<1e-4); 耦合无差异; state=h02_complete, 报告 07-quality/H02-phase-space-coupling.md |
| P021 | bbbd H03 扫视微结构 (连续8简报空转) | 2026-08-12 | 21:15 in-run 执行 COMPLETE: 扫视率 分心↓ 2.31→1.50Hz (d=-1.80, p<1e-4) + 中位时长 28.8→70.2ms (d=+0.60, p<1e-4) + 幅度中位 分心↓ (d=-0.47, p=0.04); state=h03_complete, 报告 07-quality/H03-saccade-microstructure.md |
| P022 | WearGait-PD 下载完成但 zip 损坏 (首传段 HC108 区) | 2026-08-13 | 00:41 下载完成 1182.9MB (v5 loop 自验 unzip rc=0 系假阳性); 复核 testzip 发现 HC108 区损坏 (本地头 323.8M/328.1M/333.5M 坏 + HC108_Balance inflate 失败, 首传段 0-333.9M 内); 01:2x GCS range 重取 305,591,946-339,555,254 (33.96MB) 修补拼接; 147 文件 CRC 全 OK; 已解压 raw/ (15 HC+14 PD × 5 任务 + 2 临床表); state.json 回写 data_ready_extracted |
| P023 | WearGait-PD H01 步态时空参数 | 2026-08-13 | 03:0x in-run COMPLETE: 12 时空/IMU 特征中仅 TandemGait 步态不对称显著 (PD 0.061 vs HC 0.018, p=0.043, d=+0.18) + 池化边缘 (p=0.053); 分类 AUC Balance 0.700 (n=17) 其余 <0.55 → 主要阴性; 年龄混杂 HC 更老 (78 vs 69, p<0.001); state=h01_complete, 报告 07-quality/h01-gait-spatiotemporal.md |

## 待解决 (Open)

| 编号 | 问题 | 严重度 | 状态 |
|------|------|--------|------|
| P010 | BPPV 论文 03-code/ 空目录 — 仿真代码缺失 | 🔴 P0 | 投稿阻塞项; 需从来源恢复或补写可复现脚本 |
| P011 | BPPV 论文正式投稿 (Elsevier EES 手动上传) | 🔴 P0 | 14项材料齐, 待人工操作 |
| P012 | state.json 管线 239/241 篇 phase=unknown | 🟡 P1 | 47天停滞, 需批量重扫描 |
| P013 | 28 篇 harvest 论文 NOT_STARTED 无评分 | 🟡 P1 | 参考论文(非产出), 可按需 quality-gate |
| P014 | 省级人才申报通道确认 | 🟡 P1 | 领军/青年/医坛新秀 待选 |
| P015 | 根分区 79% (62G 剩余) | 🟢 P2 | 持续增长需监控 |

## 误报澄清 (2026-08-07 简报)

- train_shape_net "空转" → 无真实进程, GPU 空闲正常
- evolution-state.json "丢失" → 实际存在 (Cycle 210, 0.9676)
- 文献监控 "无输出" → 今日 11 个 cron 输出正常
- Cron "last_run=never" → 22 任务全部 enabled 且正常产出
