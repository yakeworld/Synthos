# GOLDEN_SET.md — training-pipeline-audit

> 对应原则：P0（凡数必源）+ P4（假说可证伪性）
> golden_set_origin: self_defined

## 设计依据

金标准自设（`self_defined`）。设计目标：验证给定一个训练管线项目（数据清单 + 管线步骤 + 训练日志），技能能否产出 paper_plan.json（IMRaD 结构 + 文献列表 + 时间表），识别 ≥3 个精确定位的研究空白，生成 ≥3 个含检验条件与反证路径的可检验假设，且所有数值指标可追溯至训练日志。

## 测试用例表 (cases/)

| Case | 类型 | 输入摘要 | 通过标准 |
|------|------|----------|----------|
| case_001 | 正常路径 — K230 眼动训练管线 | 901 帧 K230 图像 + 976 帧 OpenEDS + 7 步 CV 管线 + MobileNetV2+T3EM 4 阶段训练日志（30+20+20+20 epoch，Val Dice=0.8955, CErr=1.63px） | ① paper_plan.json 含完整 IMRaD 结构 + 15-30 篇文献列表 + 时间表（TRAI-007）；② 研究空白 ≥3 个且每个定位到具体文献矛盾/方法缺口（TRAI-002）；③ 假设 ≥3 个，每个含 test_condition 与 falsification_path，格式符合 hypothesis-generation IO_CONTRACT（TRAI-003）；④ Val Dice=0.8955 / CErr=1.63px 有 source 字段指向训练日志行（TRAI-001） |
| case_002 | 错误路径 — 无源指标（违反 TRAI-001 数据诚实门） | 项目目录含代码 + 部分训练日志，但日志中无 Val Dice/CErr 数值，上游却声称 Dice=0.91 | 技能必须：① 拒绝将 Dice=0.91 写入 paper_plan（触发 TRAI-001 数据诚实门），在 metrics 中标注 unverified + missing_source；② 错误信息含上下文（哪个指标、应来自哪份日志）与恢复建议（重跑 validation 或补齐日志）；③ 不编造缺失指标，缺失即缺失；④ 其余可追溯字段正常输出，不因单点缺失整体失败 |

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用语义等价判定：

- IMRaD 五个 section（introduction/methods/results/discussion/conclusion）必须齐全
- 每个研究空白必须带 `located_in`（文献矛盾或方法缺口描述），不得空泛
- 每个假设必须带 `test_condition`（可执行检验）+ `falsification_path`（何种结果推翻）
- 指标必须带 `source`（日志文件 + 行号/字段）；无源指标必须出现在 `rejections`

## 通过标准

- pass_threshold: 1.00（2 个 case 全部通过）
- 理由：无源指标直接违反凡数必源铁律，不设容忍度
- 权重：TRAI-001（指标可追溯）与 TRAI-003（假设可证伪）为 critical；IMRaD 完整性与文献数量为 normal

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（K230 正常 + 无源指标错误路径） | Synthos Agent |
