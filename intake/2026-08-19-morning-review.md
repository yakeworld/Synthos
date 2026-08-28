# 战略回顾记录 (2026-08-19 09:30, 09:30 cron 轮)

## 1. 在研项目状态
- **3diris-01 (主论文)**: G28 PASS + G29 训练中 🔄
  - G28 pose 跨受试者验证: held-out pose mean r=**0.9989**, per-subject 全部 ≥0.9982, RMSE 0.0171 rad → **PASS** (≥0.90)
  - 关键发现: posed npz 自创建起就是模型级分割 (train IT001-090/val IT091-100) → G 系列 posed 验证 (n=7500) 早已跨受试者
  - G29 零曝光重训: 09:07 启动 (h5_g29.py, ~5-6h), 正面池限 IT001-090, val IT091-100 零曝光
  - 论文 59 页 0 errors; G14 OpenEDS ⛔ 认证墙 (第 15 轮)
- **dual-system-mocap-gait (P1)**: H01 FAIL ❌
  - 数据布局探针 ✅: 21 受试者, TRC 120Hz 39-marker + COCO-17 17-kp (front/side), xlsx metadata
  - **H01 系统误差表征: FAIL_plane_assumption** — knee RMSE 107.8°, r=0.187, 无一致模式
  - 根因: 2D 投影丢失深度 + 单目透视畸变 → 平面假设根本失效
  - H02 候选: (a) 双视角 3D 三角测量 (b) 尺度不变指标 (c) 透视校正 — 待 ROI 评估
- **rehab-stroke-kinematics (P0.5)**: H01 COMPLETE ✅
  - FM 基线: 222 samples × 5670 feat, Ridge 5-fold subject CV, **overall r=0.8445 / R²=0.6961**, 27/27 subscores r>0.5
  - 下一步: 数据字典表 + 可扩展模式 #61 记录 (文档工作, 非计算)

## 2. 新机会
- 无新扫描 (本轮专注 MoCap H01 执行)
- 上轮 tracked 维持: GLEAM (Kaggle 凭证), Birdshot (DUA), LAIA (链接待核验)

## 3. 方向判断
- **3diris G29 是关键节点**: 若 PASS → G 系列跨受试者泛化彻底闭合 (G26 FAIL → G27 PASS → G28 PASS → G29 验证), 论文进入打磨阶段
- **MoCap H01 FAIL 是诚实结果**: 2D 平面角对比不可靠不是 bug, 是方法学限制。H02 需 3D 重建才有意义, 投入产出比待评估 (P1 项目, 不阻塞 P0)
- **rehab r=0.8445 是强基线**: 27/27 动作 subscores 全 >0.5, 论文级结果; 数据字典 + 模式 #61 是低成本高价值收尾

## 4. 阻塞项 (需人工)
1. ImmerIris 申请邮件发送 (草稿 intake/immeriris-application-email.md, 最高优先)
2. GLEAM / G14 OpenEDS: Kaggle 凭证
3. Birdshot-Wide: Zenodo 受控访问申请 (需 DUA 签署)
4. 期刊指定 (3diris 59 页篇幅平衡前置)

## 5. 派发 / 本轮完成
- ✅ dual-system-mocap-gait: 数据探针 + H01 全量执行 + FAIL 记录 + state 更新
- ✅ G29 由 cron 覆盖 (09:07 启动), 未重复派发
- ⏳ G29 收束: 下次 cron (~14:30) 检查 g29_results.json
- ⏳ rehab: 数据字典表 (下轮)
