# 战略回顾记录 (2026-08-18 00:10, 12h 周期)

## 1. 在研项目状态
- **3diris-01 (主论文)**: G25c 训练中 ✅ 健康
  - proc 2522663 (h5_g25c.py, 7.5h+, 826% CPU, GPU 32%/4.4GB) + watchdog 2522764 存活
  - 00:08 时 ep 62/100, ~430s/ep → ETA ~04:35
  - 指标: tr=0.0531, va=0.0369, PCA-r=0.9896, Pose-r=0.9970, inv drift 0.1154 稳定, var=0.0002 (方差保持生效, G25 坍缩未复现)
  - 预注册判定目标不变: clip5&7 no-norm pose r≥0.90 / clean Δr<0.01 / frontal ≤0.05 rad
  - **完成链全自动**: h5_g25c.py 结束 → run_g25c_chain.sh 自动跑 analyze_g25c.py → degradation 电池 → 两个 results JSON 齐后 watchdog 退出; 3diris-autonomous-research cron (04:00/08:00) 接手 Fig26 + G25 论文章节
- **3diris-02 (dilation)**: 决策 RECOMMEND-MERGE 维持, 无活跃工作 ✅
- **3diris-03 (cnn-vs-sfm)**: 决策 DEFER 维持 (SfM 对比待 3diris-01 投稿后评估) ✅
- **3diris-04 (sim2real)**: g24b_complete, quality 82, 51 页 0 errors ✅ 完成态

## 2. 新机会
- **ImmerIris (P0.5, 最高优先)**: 邮件草稿已就绪 (intake/immeriris-application-email.md, 中英双版) ⛔ 发送阻塞: 无 SMTP/himalaya 配置 → **需人工发送** (yakeworld@shu.edu.cn → yxmi20@fudan.edu.cn)
  - Benchmark 协议 (Google Drive 1j8oTcBEyCh4KMu3-Gn5gbxvG_fI6jdOP): 直连超时 + 代理池 HTTP 000 → ⛔ 网络阻塞, 需人工/VPN 下载
  - GitHub 核验: NiborPolaris/ImmerIris 30⭐, 官方页确认, 协议在 Drive
- **HeyJay! (PD 语音)**: P1, 待下轮文献监控评估 (Neuro-Logical/HeyJay 规模/许可)
- **GazeXPErT / MSN-TCSeg / VS 纵向**: 维持追踪, 无新变化

## 3. 方向判断
- G25c 是部署鲁棒性线最后一块拼图; PASS → 该线彻底闭合, 转入论文打磨 (51→目标篇幅, 需用户指定期刊); FAIL → 采集侧曝光控制分析 (G26)
- G14 OpenEDS ⛔ 维持: 需用户 Kaggle/Facebook 凭证 (第 11 轮确认 404/认证墙)
- 3diris-02/03 决策正确, 不消耗资源

## 4. 阻塞项 (需人工)
1. ImmerIris 申请邮件发送 (最高优先, 草稿在 intake/)
2. ImmerIris benchmark 协议下载 (Google Drive 不可达)
3. G14 OpenEDS 凭证
4. 期刊指定 (论文篇幅平衡前置)

## 5. 派发
- 本轮无新派发: G25c 完成链已由 watchdog + 3diris-autonomous-research (08:00) 覆盖
- 12h 后复查: G25c 判定结果 + ImmerIris 邮件状态
