# Synthos 问题跟踪 (PROBLEMS.md)

更新时间: 2026-08-16 (cycle-213 dsh-headless 全链路跑通: PRECHECK→DIAGNOSE→DISPATCH→VERIFY→RECORD; 捕捉 dsh 自欺 1 文件; 脏文件陷阱实测; P035 登记; P034 dsh-self-evolution 链接已补; P033 边界待用户裁决)

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
| P024 | WearGait-PD H02 关节运动学指纹 | 2026-08-13 | 06:1x in-run COMPLETE: 60 运动学特征 (13 IMU Pitch/Roll ROM+std + 膝/髋/踝关节角 + 不对称) raw 0 显著; 年龄校正 (OLS feat~age+group) 仅 2/60 (L_DorsalFoot_Roll p≈0.019, 判机会); 关节角全不显著; AUC kin_core=0.300 < age_only=0.844, kin+age=0.700 → 运动学无超年龄判别力; 预注册 REJECT; state=h02_complete, 报告 07-quality/h02-joint-kinematics.md |
| P025 | eye-tracking-autism H01 扫视/注视参数化 | 2026-08-13 | 12:2x in-run COMPLETE: 1.26M 行/57 被试 (27 ASD/30 TD); 8 特征仅 fixation_med_dur raw 显著 (ASD 218.9 vs TD 258.6ms, p=0.014, d=-0.41), 年龄校正后 p=0.077 消失; AUC age_only=0.454/kin=0.492/kin+age=0.452 全≤随机 → 预注册 REJECT; 25.csv 为异格式排除; state=h01_complete, 报告 07-quality/h01-saccade-fixation.md |
| P026 | 3diris G17 训练链反复静默死亡 (3次: Ep34/53/13) | 2026-08-15 | G17 收官 01:01 (100ep, best val 0.0262, PCA r=0.9908, f=0.05 判词: 最小前置比例 r≥0.95); crash-resume + 分离 watchdog 方案验证成功; 论文重编译 0 错误 |
| P027 | WearGait-PD H03 相空间复杂度 (连续2+轮空转) | 2026-08-16 | 00:1x in-run COMPLETE: 20 特征 (5 通道 FreeAcc_U × SampEn/Higuchi/LLE/corr-dim) subject-level LR AUC=0.844 PASS (folds [0.89,0.67,1,1,0.67]); age_only=0.911, feats+age=0.967 (+0.056 增量); 核心: 踝部复杂度 PD↓ (L_Ankle SampEn d=-1.48 校正p=0.006, corr-dim d=-1.49 校正p=0.013; R_Ankle SampEn d=-0.98 校正p=0.001); 10/20 年龄校正显著 — 首个强信号, 与 H01 阴性/H02 REJECT 对照; state=h03_complete, 报告 07-quality/h03-phase-space.md |
| P028 | 3diris G22 Fig22 缺失 (chain 假完成) | 2026-08-16 | 07:12 in-run 修复: analyze_g22.py L225 `'coral-o'` 非法 fmt → `color='coral',marker='o'`; Fig22 重新生成 (PNG/PDF), 拷贝至 3diris-04/05-figures, sim2real 论文重编译 0 errors (paper.pdf 6.5MB); G22 结果: f∈{0.10,0.25,0.49} 无坍缩 (posed pose-r 0.9930/0.9928/0.9934, PCA-r 0.9922/0.9949/0.9966), frontal pose pred ~0.003 rad < 0.10 目标 → UNMASKED 下坍缩阈值 f*>0.49 |
| P029 | 3diris G23 Fig23 缺失 (chain 假完成, P028 同型) | 2026-08-16 | 15:39 chain 报 complete 但 analyze_g23.py L250 `np.mean(dict)` TypeError (G20 inf JSON pose_mean_abs_pred 为 dict 非 list) → JSONs 已存但 Fig23 未生成; 16:10 in-run: patch L250 + finish_g23.py 复用 JSON 重出 decision+Fig23; G23 结果: contrast-aug U[0.5,1.5] 47ep 早停 best val 0.0509, clean posed pose-r 0.9983 (+0.0013 vs G20 PASS), contrast×0.7 pose r 0.526→0.733 (×0.5: 0.628→0.813) — 大幅改善但仍 <0.90 预注册阈 → **FAIL: G21 对比度归一化仍为部署必需**, 增强训练为互补 (14 条件全支配); 16:00 3diris 槽已写 G23 章节但 caption `\\` 前有 `\label` bug → 已修; paper.pdf 47 页 0 errors; state=g23_complete |
| P038 | GSTRIDE H02 脆弱性轨迹 (DDBB x IMU) 连续2轮简报空转 | 2026-08-27 | 10:0x in-run 执行 **PASS**: N=163 (frail Fried>=3 n=21), 34 特征 (17 cv+17 std) 年龄校正 OLS + BH-FDR: 8/34 显著 (fdr 0.009-0.017, 全部负向 d 0.97-1.50: frail 变异性更低, 方向异常需临床解读); AUC age_only 0.637 / feats+age 0.806 (+0.169 增量); SPPB 21/34 + TUG 22/34 FDR 显著 (stride velocity std p<1e-11), FES-I/GDS 阴性; state=h02_complete, 产物 07-quality/h02-frailty-trajectory.{json,md} + 03-code/h02_frailty_trajectory.py |
| P039 | GSTRIDE H02 论文骨架连续3轮简报计划空转 (21:00 轮为第3次承诺) | 2026-08-28 | 22:0x in-run COMPLETE: 01-manuscript/paper.tex (IMRAD 全文骨架: abstract/CARS intro/methods/results Table1 8特征/discussion S&F四步/data availability); pdflatex x2 0 errors, paper.pdf 4 页 172KB; state.json=h02_complete_manuscript_skeleton; 余: references.bib (TO-FILL cite keys, 目标>=30 refs 含 PDF) + 人口学表 + 图. **08-29 06:0x in-run 续**: references.bib 补至 32 条全 Crossref 实证 (30 新条目含 TUG/Higuchi/Richman/Hausdorff 经典, 0 虚构); pdflatex+bibtex 全链 0 undefined citations 0 errors, PDF 4p 177KB; 30 DOI PDF 下载 doi-fetch 后台循环已启动 (bib=PDF 铁律待下载收尾); 人口学表+图仍待 |
| P037 | LEOPs ERG 数据集 (Mendeley doi 10.17632/w3yx7hdds7.1) P0.5 立项 | 2026-09-05 | **数据就绪 (09-05 03:0x in-run 核验+回写)**: 09-04 01:18 下载完成 130.6MB; 嵌套 zip 结构, testzip 双层全过; 814 文件解压至 raw/LEOPs/ (xlsx 47.4MB + jsons/253 + ImagesERG/558 PNG), 0 缺失; state=data_ready_extracted. **06:0x in-run H01 执行 (预注册 04:xx 落盘)**: 253 被试 (ASD(+ADHD) 96 vs Control 157, 年龄 5.0-35.1), jsons 预计算特征 (a/b 波幅值+潜伏期, 3 协议 12 特征), 被试级中位聚合+年龄 OLS 校正: 4 项校正后显著 (LA3_b_time p=0.0086 d=+0.42 / 9_step_b_time p=0.0278 d=+0.37 / LA3_b_amp p=0.0398 / 9_step_b_amp p=0.0493 均 d≈-0.28), Bonferroni 0 存活; AUC 5-fold: age 0.471 → feats+age 0.583 (+0.112 增量); 家族一致性: b_amp 三协议同向 (ASD 幅值降低) 成立, b_time 方向不一致 → **PARTIAL (弱阳性, 非混杂型 REJECT)**; 三分敏感性 LA3_b_time p=0.0026 一致; 产物 03-code/h01_erg_family.py + 07-quality/h01-erg-family-{results.json,report.md}, state=h01_partial; 余: OPs 特征+FSIQ 子样本 (n=63)+站点分层+BH-FDR 复核 |
| P036 | REHAB 数据集 (Sci Data 08-05, 120 例卒中) P0.5 立项: 数据已下载解压就绪 (737MB rar, 1.2GB raw, 36,110 npy, 2026-08-18 05:12); 探针误读 27/16 为受试者数 | 2026-08-18 | **08:1x in-run feasibility 核验 PASS**: 27/16 = 评估/训练 MOVEMENT 数 (非受试者) — 论文 (s41597-026-07802-2) + Label.npy (222,27) 实证: 120 例 (60 实验+60 对照) → 222 次 Fugl-Meyer 评估 × 27 动作 × 3 传感器 = 17,982 npy, 数据完整无缺失; 训练数据 16 动作 (d×880×6); FM 临床标签齐备 → 监督学习可行; state=feasibility_done, 空白: FM 自动评分 + WearGait-PD 方法族复用 |

## 待解决 (Open)

| 编号 | 问题 | 严重度 | 状态 |
| P040 | 评估器奖励完整性: 实验1完成 + 全量重扫基线 | 🟡 P1 | 2026-09-07 实验1: 三处假阳性已修 (f9c2963d+补丁2), 冻结反例 7/7. 新口径全量重扫(99篇有tex): **overall pass=0** (旧state声称80篇pass全部翻FAIL), G2真编译33篇fail (缺图/xeCJK/真语法错误), L0.5 0/99 — 数据层实证: state.json 是管线状态非数值溯源台账, 论文实验数值未入 state.json (最好14篇也仅50-99%匹配). 这是数据缺口非门过严, 保持门不动(防选有利指标). 余: (a)数值溯源台账批量回填 (03-code/04-data → state.json, 机械任务可cron批跑) (b)33篇G2真编译错误修复 (c)评审脆弱点3/4/5=实验2 (d)1篇bppv-pinn GB编码异常 (e)76篇无tex(harvested)不在过闸范围 |
|------|------|--------|------|
| P030 | dsh 与并行 cron 同库编辑竞态: cycle-211 期间 11 个 private 技能被并行 cron 同时修改, dsh 报告 (15 changed) 与实际 diff (4) 不一致 | 🟡 P1 | 已缓解: 独立 VERIFY 捕获并归因 (cycle-211 记录); 后续 dsh 周期派发前检查并行 cron 状态, 或 commit 时按 diff 归属拆分 |
| P034 | dsh 技能自动发现仅认 ~/.dsh/skills 目录 (用户实测指正); customSkillDirs (skills-flat) 未被自动发现消费 | 🟡 P1 | 文档已修正 (commit bf153d4); **cycle-213 已补 dsh-self-evolution 缺失链接 (1/11, 实测进 dsh 目录可见)**; 其余 10 个缺失链接待核对补齐 |
| P032 | 9 个 SKILL.md 正文为重复两段式结构 (同一内容出现两次, 疑似历史合并事故; dsh cycle-212 发现) | 🟡 P1 | **cycle-213 dsh 执行体再次独立确认 10 个目标文件存在重复块** (citation-appropriateness-verification/knowledge-base-audit/ode-simulation-tuning/synthos-akne-bridge/dataset-discovery/kg-bridge/citation-bib-crossref/skill-absorption/system-bridging/literature); dsh 只在首个块插入原则, 未触碰重复块; 待独立去重轮 (批量 Python 去重 + 语义核对后 commit) |
| P033 | skills/private/ 被 .gitignore 忽略且 0 文件入库: 13+ 个 private 技能仅存在于工作区与 symlink 链路, git 无备份; 隐私策略与文档缺口 | 🟡 P1 | **cycle-213 实测发现 skills/private/ 有 9 个技能仍在 git index 中 (未被 12cf791 清除); cycle-213 commit 6bee73a 把这 9 个的修改也提交了 (原则小节, 方法论内容, 非敏感)**; 待用户裁决隐私边界 (纳入 git 含隐私扫描 / 保持 ignore); **裁决前 dsh 周期 RECORD 只提交 public 技能, private 原则改进留在磁盘**; **cycle-214 实测后果: 14 个 private 原则改进未提交 => 计为 dirty => structural/absorption 被拉低, OVERALL 0.9892->0.9660 (非质量回归, 是 P033 测量假象; 原则改进真实, optimize 0.9408->0.9599 上升); 裁决选项: (a) 纳入 git 含隐私扫描 => 可提交 => 测量恢复; (b) 保持 ignore => 需 diagnose.py 的 dirty 计数排除 skills/private/ (评分策略, 归宪法/用户, 引擎不自改)** |
| P035 | .gitignore 忽略 /evolution-state.json 与 /evolution-log.md → 违反 "git 即记忆" (cycle 186+ 状态文件游离于 git 外, git 内为旧快照; state.git_commit 漂移 ebce66e ≠ HEAD) | 🟡 P1 | cycle-218 发现; 临时处置: `git add -f` 强制入库当前版本 (050266f); **待裁决**: (a) 改 .gitignore 允许两文件入库 (推荐, 与 git-as-memory 一致); (b) 保持 ignore, 对账脚本每次 force-add; (c) 移出根目录 (改变约定) |
| P010 | BPPV 论文 03-code/ 空目录 — 仿真代码缺失 | 🔴 P0 | 投稿阻塞项; 需从来源恢复或补写可复现脚本 |
| P011 | BPPV 论文正式投稿 (Elsevier EES 手动上传) | 🔴 P0 | 14项材料齐, 待人工操作 |
| P012 | state.json 管线 239/241 篇 phase=unknown | 🟡 P1 | 47天停滞, 需批量重扫描 |
| P013 | 28 篇 harvest 论文 NOT_STARTED 无评分 | 🟡 P1 | 参考论文(非产出), 可按需 quality-gate |
| P014 | 省级人才申报通道确认 | 🟡 P1 | 领军/青年/医坛新秀 待选 |
| P015 | 根分区 79% (62G 剩余) | 🟢 P2 | 持续增长需监控 |
| P037 | dsh 自进化周期两个实测陷阱 (cycle-213): (a) 脏文件陷阱 — commit 前跑 diagnose 读到 0.958 (未提交改动计为 dirty 拉低 structural/absorption), commit 后读到 0.9892; (b) dsh 自欺 — headless 声称 15/15 但 knowledge-acquisition 未写入 (独立重算 14/15 捕获, 父 Agent 修复) | 🟡 P1 | 已缓解并固化: RECORD 纪律改为 **commit-first-then-measure**; VERIFY 独立重算 (禁复用 dsh 报告) 已实际捕捉自欺; dsh 任务 prompt 加入"逐文件 grep 自检, 勿假设成功报 true" (cycle-214 起) |

## 误报澄清 (2026-08-07 简报)

- train_shape_net "空转" → 无真实进程, GPU 空闲正常
- evolution-state.json "丢失" → 实际存在 (Cycle 210, 0.9676)
- 文献监控 "无输出" → 今日 11 个 cron 输出正常
- Cron "last_run=never" → 22 任务全部 enabled 且正常产出
