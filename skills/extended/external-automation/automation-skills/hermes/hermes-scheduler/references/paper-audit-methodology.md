# 论文管线审计 — 论文质量检查覆盖率审计方法

## 触发条件
- 需要全面审计outputs/papers/下所有论文的质量检查状态
- 怀疑cron任务的质量检查覆盖率异常低
- 需要给领导/团队汇报论文管线健康状态

## 审计流程（5步）

### Step 1: 论文状态扫描
遍历outputs/papers/下所有目录，对每个目录检查：
- state.json是否存在
- state.json中的steps_completed包含哪些
- current_step是什么
- 有paper.tex吗？
- 有paper.pdf吗？
- 有references.bib吗？
- 有step_quality_check.md吗？
- 有quality_score吗？
- 文件总数和目录深度

### Step 2: 分类
将论文分为：
- **完整管线**：state.json + steps包含所有关键阶段(gap_analysis, abstract, results, reference_check, quality_check) + tex + bib
- **半截管线**：有state但steps不全
- **有文件无state**：有tex/bib/pdf但无state.json
- **空目录**：无实质内容

### Step 3: 质量检查覆盖统计
- 总论文数
- 有完整管线的论文数及其中通过质量检查的比例
- 有半截管线的论文数
- 有文件无state的论文数
- 空目录数

### Step 4: 问题识别
- 哪些论文管线完整但quality_score未写入state.json？
- 哪些论文的step_quality_check.md分数格式不统一？
- 哪些论文有quality_check步骤但current_step不是complete？
- 哪些论文完全缺失引用检查？

### Step 5: 修复建议
- 对管线完整但无score的论文：先解析step_quality_check.md写score
- 对管线完整但quality_check未执行的论文：先执行G1-G7闸门
- 对有文件无state的论文：判断是编译产物还是半成品，分类处理
- 对空目录：清理

## 输出格式

审计报告应包含：
- 总体统计（总数/完整管线/半截管线/空目录）
- 质量检查覆盖率
- 各分类论文列表
- 关键问题描述
- 修复建议

## 实战数据（2026-06-11）

| 分类 | 数量 | 占比 |
|------|------|------|
| 真正通过质量检查 | 2 | 1.1% |
| 管线完整但无score | 65 | 36.3% |
| 有文件无state | 97 | 54.2% |
| 空目录/杂物 | 3 | 1.7% |
