# 战略回顾执行报告 — 2026-08-22 12:00 (12h 周期)

## 1. 状态扫描

### 训练进程
- `pgrep -f train_shape_net.py`: 无进程 (符合预期 — 合成域 G 系列 08-20 全收束后无新训练; 该脚本仅存于 /mnt/nfs/Synthos_back 旧快照, 现行工作区为 sda2)
- 无 GPU 训练进程; iris_gui.py (专利标注工具) 运行中 (用户侧专利线活跃)

### 3diris 集群 (主线)
- **3diris-01** (q=80): stage=g33_single_frame_identity_fail_paper_74p; 论文 74 页 0 errors 0 undefined (08-20 编译); G 系列校准线 G27-G33 双闭合; **阻塞: G14 OpenEDS (~/.kaggle 仍空, 无 kaggle.json, 08-22 复测维持) + 期刊选定**
- **3diris-02/03**: ghost_backfilled (占位, 不推进)
- **3diris-04** (q=82): g33 同步, 论文 74 页; 部署鲁棒性线 CLOSED
- **本轮关键发现**: TEyeD (287GB) 已全量在本地 /mnt/nfs/TEyeDSComplete (Dikablis 157G / GazeinTheWild 98G / NVIDIAGazeDS 30G / LPW 2.2G; 423 视频 + 15,477 标注文件) → 54.6-4 "TEyeD 官方源下载核验" 待办实质闭环 → **新立项 teyed-3d-eyeball-audit (P1)**

### 步态方法族 (自动推进主力)
- **treadmill-steady-gait-kinetics**: h03_complete — H 系列收官 (H01 相空间 3 显著 + 速度梯度; H02 慢速髋 ROM Old>Young 与 PD 方向相反 = PD/衰老鉴别维度; H03 踝跖屈功率 Old↓ 速度依赖 + 远端→近端代偿 = PD 动力学鉴别指纹) → 短文素材齐备 (Data in Brief 框架)
- **normative-gait-fall-tracking**: h01_complete (08-22 01:08) — 10MWT 5 年龄带 × 时空/相空间: 全 ns (0.08-0.19 边缘, 年龄带间无显著年龄趋势) — 诚实阴性; H02 跌倒标签仍缺 (仓库无终点列)
- **gaitintent / mobilityapp / eog-od12 / rehab**: 各 h 系列闭环或写作假设待决策 (同 08-21 午间)
- **dual-system-mocap-gait**: h01_complete_fail (2D 平面角不可靠) — H02 ROI 决策待 PI/用户

### 文献监控
- 3diris-thinking.md 更新至第 54 轮 (08-22 09:00): 净新增 5 数据集 (EATMINT 19.1G / MultiPENG 14.2G / DR(eye)VE Mini / PD AlphaPose JSON / 情绪眼动待核验) + 4 信号; 新可扩展模式 #74 药物态双模族 + #75 交互任务耦合族 (场景梯度成型)
- BPPV 零新增第 28 轮 → 自创数据集路线维持; OpenEDS 零新增延续

## 2. 新机会
1. **⭐ TEyeD 本地全量 → 已立项 teyed-3d-eyeball-audit (P1)**: 真实 3D 眼球/虹膜标注审计 + 跨域形状验证 = G14 前置真实域证据线 (G14 本身仍等 kaggle.json, 但 TEyeD 提供替代真实域通道); H01 数据审计已 READY (自包含, 只读小 txt)
2. MultiPENG / EATMINT (#75 族): 14-19GB 下载量大, sda2 余量 53G 可容但两项目合计超限 → 先 TEyeD, MultiPENG 列次优先 (待 TEyeD H01 完成后评估磁盘)
3. FOGBRAD (Zenodo 0 文件附件) / 36875659 (figshare 403 复测维持) → 通道仍阻塞, 08-27 复查顺延

## 3. 方向判断
- **方向正确, 无需调整优先级**。主线: 3diris-01 投稿准备 (期刊选定为唯一人工卡点) + 步态族短文收束 (treadmill 素材已齐)
- 本轮自动解锁: TEyeD 真实域通道 (原"等下载核验"待办 → 已实证在本地, 无需再等外部)
- 需人工 (维持 08-21 清单, 无新增): ① kaggle.json (G14) ② 期刊选定 (3diris 74 页打磨前置) ③ BPPV 投稿 P010/P011 ④ P033/P035 隐私裁决 ⑤ P014 省级人才申报 ⑥ dual-system-mocap H02 ROI 决策
- 磁盘: 根 80% / sda2 85% (53G 余量) — 新立项只读审计不增盘, 但 MultiPENG/EATMINT 两项目不可同时下载, 需串行

## 4. 新派发任务
1. **teyed-3d-eyeball-audit H01 数据审计** — 已建目录 + state.json (outputs/papers/teyed-3d-eyeball-audit/): 抽 NVIDIAGazeDS 10-20 记录解析 eye_ball/gaze_vec/iris_lm_3D/eye_movements, 统计 validity/不精度/事件占比 → 数据字典 + 质量报告; 自包含, 下个 hourly-briefing 可捡起执行
2. **3diris-01 todo.md 更新** — 记录 TEyeD 解锁 (G14 替代通道) + 本轮巡检状态
3. 待办延续: treadmill 短文写作决策 / normative H02 (跌倒标签核验) / PhysioNet + MSN-TCSeg 08-27 复查 / P012 批量重扫
