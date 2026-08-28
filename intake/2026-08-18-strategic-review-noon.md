# 战略回顾记录 (2026-08-18 12:00, 12h 周期)

## 1. 在研项目状态
- **3diris-01 (主论文)**: stage=g25c_complete ✅ G25c PASS (2026-08-18 04:35)
  - clip5/clip7 no-norm pose r=0.9628/0.9435 (≥0.90), 干净域无回退, frontal bias 0.0088 rad
  - 部署鲁棒性线 G06-G25c 全部收束; paper 54 页 0 errors
  - **G26 (cross-subject generalization) 已由属主 cron 12:21 启动** (h5_g26.py, model-level split 90/10, 11.24M params)
  - G14 OpenEDS ⛔ 认证墙 (Kaggle/Facebook 凭证, 延续 14 轮)
- **3diris-02 (dilation)**: ghost_backfilled, RECOMMEND-MERGE 维持, 无活跃工作
- **3diris-03 (cnn-vs-sfm)**: ghost_backfilled, DEFER 维持 (SfM 待 01 投稿后评估)
- **3diris-04 (sim2real)**: 54 页 0 errors (含 G25 章节), 完成态
- **rehab-stroke-kinematics (P0.5, 今晨立项)**: feasibility_done (08:23)
  - 数据: 315MB rar → 1.2GB, 36,110 npy, 222 FM 评估 × 27 动作, Label.npy (222,27) 确认
  - **H01 FM 基线已派发 (12:28 detached 启动)**: 5670 特征 → Ridge 5-fold CV, ETA ~35min
- **dual-system-mocap-gait (P1, 本轮新立项)**: scaffold + state.json + 下载启动 (12:24)
  - Zenodo 19720803 CC-BY-4.0, 1140MB (654+486MB), 下载中 ~1.5MB/min, ETA ~7h

## 2. 新机会 (第 39/40 轮)
- **GLEAM 三模态青光眼 (P0.5, 第40轮最高优先)**: Kaggle zhangyiyinge/gleam-dataset (页 200 ✅) + GitHub microewing/HAMM ✅
  - ⛔ 下载需 Kaggle 凭证 (同 OpenEDS 认证墙) — 结构-功能一致性矩阵短文待凭证解锁
- **PCO-IOL (P1, 第39轮)**: figshare API 403 (数据中心 IP 被封) + Tor 超时 → 链接未确认, **不立项** (§1d5)
- **Stumble-IMU-sEMG (P1)**: 仓库链接未确认 (Zenodo 无直接命中) → 不立项, 维持监控
- **Birdshot-Wide (P0.5)**: Zenodo 受控访问 (需申请+DUA) → 可提交申请但需人工决策
- **CADMUS/RAMSEs**: INSIGHT 受控访问族, 记录申请条件, 不投入管线
- **LAIA 合成驾驶眼动**: 仓库链接待核验 (下轮)

## 3. 方向判断
- 3diris 集群: G 系列收束后正确进入 **cross-subject 泛化** (G26), 符合"真实数据不可得 → 合成域泛化验证"路径
- 眼域新机会集中在**多模态配对/临床大数据**轨道 (GLEAM/PCO-IOL/Birdshot) — 与 3diris 形态学族互补
- 前庭/BPPV 域 14 轮空白维持 → 自创数据集机会不变
- **候选启动缺口**: 全部需要 Kaggle/figshare 凭证或人工申请 — 无凭证解锁则自动管线保持现状

## 4. 阻塞项 (需人工)
1. ImmerIris 申请邮件发送 (草稿 intake/immeriris-application-email.md, 最高优先)
2. GLEAM / G14 OpenEDS: Kaggle 凭证
3. Birdshot-Wide: Zenodo 受控访问申请 (需 DUA 签署)
4. 期刊指定 (3diris 54 页篇幅平衡前置)
5. paper-harvester 08:47 超时失败 — 8 篇已 in-run 补收割 (4 PDF 归档)

## 5. 派发
- ✅ dual-system-mocap-gait 立项 + 下载启动 (12:24)
- ✅ rehab H01 FM 基线启动 (12:28)
- ✅ 8 篇 harvest 补建 (4 PDF + 4 待手动)
- ✅ G26 由属主 cron 覆盖 (12:21), 未重复派发
- 12h 后复查: G26 结果 + H01 基线 + MoCap 下载完成 + GLEAM 凭证
