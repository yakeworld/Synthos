# 战略回顾记录 (2026-08-19 12:30, 12h 周期 cron 轮)

## 1. 在研项目状态
- **3diris-01 (P0, 主论文)**: G29 零曝光重训 🔄 进行中 (PID 3467953, h5_g29.py, 09:07 启动)
  - ep 25/100 (12:09 时点), ~7.3 min/ep → ETA ≈ 21:15
  - 中期轨迹: pose-r 0.9905-0.9921 (预注册 PASS 阈值 0.90 已超), PCA-r 0.68-0.71 (<0.90 → 指向"G 系列 posed PCA 是曝光记忆"预期结论)
  - watchdog 存活 (PID 3468054); GPU 0 活跃 (87% util)
  - G28 已 PASS (held-out pose r=0.9989, RMSE 0.0171 rad); 论文 59 页 0 errors
  - G14 OpenEDS ⛔ 认证墙 (第 15+ 轮)
- **3diris-04 (sim2real)**: g24b_complete — 部署鲁棒性线 CLOSED (14 条件 pose r≥0.910, 残差=动态范围削波)
  - 下一步: G14 (同认证墙 ⛔) / G20-G24 段落校对 (需期刊指定) / G25 contrast-aware (已被 3diris-01 G25c 覆盖)
- **3diris-02/03**: ghost_backfilled (占位, 非活跃)
- **rehab-stroke-kinematics (P0.5)**: H01 PASS (r=0.8445, 27/27>0.5) — **本轮完成收尾**: 数据字典落盘 (04-data/fm-feature-dictionary.md) + 模式 #56 记录 (3diris-thinking.md 42.7, 修正原 #61 误记)
- **dual-system-mocap-gait (P1)**: H01 FAIL_plane_assumption (诚实结果) — H02 三候选待 ROI 评估, 不阻塞 P0
- 其余 ~120 篇: publication_complete / harvested (文献收割, 非活跃)

## 2. 新机会
- **STAGE (模式 #66, 最高优先)**: hdmilab.cn 本机 curl HTTP 000 (网络不可达) → 下载通道核验仍需浏览器/人工; Kaggle GLEAM + OpenEDS 镜像均 reCAPTCHA 墙 → 凭证阻塞确认
- **MSN-TCSeg**: Zenodo 18376539 files=0 连续 2 轮 — 08-27 复查 (8 天后)
- **FoG-Ego / GVS-Latent**: 核验顺延 — web_search/web_extract 工具不稳定延续 (DaemonThreadPoolExecutor 错误)
- **BPPV/眩晕空白**: 16 轮维持 → 自创数据集路线不变 (模式 #65 + #68)
- **G29 判别证据 (运行中)**: PCA-r~0.70 <0.90 → 预期结论"形状跨受试者不泛化 (subject-specific), pose 跨受试者泛化 (G28)" — 清晰可发表的机制发现

## 3. 方向判断
- 3diris-01 主线正确, G29 是关键节点: 收束后跨受试者泛化章节闭合, 论文进入收尾。方向无需调整
- 3diris-04 依赖 G14 (阻塞) 或期刊指定 (人工) — 保持现状, 不新增计算
- 新项目启动: STAGE/GLEAM 联合 dataset-feasibility 是唯一"解锁即启动"候选, 但全依赖浏览器/凭证 — 维持待命
- 可穿戴运动学族 (REHAB + WearGait + MoCap) = 模式 #56 第二实例已记录, 方法族沉淀完成

## 4. 阻塞项 (需人工)
1. G14/OpenEDS + GLEAM: Kaggle/Facebook 凭证 (第 15+ 轮)
2. ImmerIris 申请邮件发送 (草稿 intake/immeriris-application-email.md)
3. Birdshot-Wide DUA 签署
4. 期刊指定 (3diris 59 页篇幅平衡前置)
5. STAGE hdmilab.cn 浏览器核验 (本机 curl 不可达)

## 5. 派发 / 本轮完成
- ✅ rehab 数据字典落盘 (fm-feature-dictionary.md) + 模式 #56 记录 + state.json 修正
- ✅ 机会核验: STAGE/Kaggle/OpenEDS 通道状态再确认 (均阻塞或需人工)
- ⏳ G29 收束: 下轮 (~21:15 后) 检查 g29_results.json → Fig30 + 论文 G28/G29 小节 + Conclusion
- ⏳ dual-system-mocap-gait H02 ROI 评估: 判断任务, 建议下轮由 PI 决策
