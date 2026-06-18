# Cron Compliance Audit — Cron任务合规性审计方法学

## 触发条件
- 怀疑cron任务未按设计流程执行
- 需要全面评估所有cron任务的健康状态
- 发现论文质量检查覆盖率异常低（如1.1%）
- 发现多个cron任务引用不存在的skill

## 审计流程（5步）

### Step 1: 全量cron任务清单获取
```bash
hermes cron list 2>/dev/null
```
收集每个任务的：job_id, name, skill(s), prompt, schedule, last_status, last_run_at, enabled

### Step 2: Skill存在性验证
对每个cron job引用的skill，检查是否存在：
```bash
# 检查Synthos/skills/
find /media/yakeworld/sda2/Synthos/skills -name "SKILL.md" | xargs grep -l "^name: <skill_name>"

# 检查~/.hermes/skills/
find ~/.hermes/skills -name "SKILL.md" | xargs grep -l "^name: <skill_name>"
```
不存在的skill = 任务空转报错。

### Step 3: Prompt-vs-Implementation对比
1. 从cron output日志提取prompt（`~/.hermes/cron/output/<job_id>/<timestamp>.md`）
2. 读取对应SKILL.md
3. 对比执行步骤是否一致
4. 关键检查项：
   - 是否要求skill_view()调用
   - 是否实现G1-G7闸门检查
   - 是否记录pipeline_trace
   - 是否有Layer A+B双质量检查
   - 是否对不通过的论文执行修订循环

### Step 4: 执行日志分析
```bash
# 查看最近N次执行
ls -lt ~/.hermes/cron/output/<job_id>/ | head -20
cat ~/.hermes/cron/output/<job_id>/*/... | head -500
```
识别模式：
- 空跑：每次都输出相同内容
- 错误：每次都报告skill not found
- 完成：每次都输出"All tasks completed"

### Step 5: 质量检查覆盖率统计
遍历outputs/papers/下所有论文，分类：
- 完整管线（state.json + 所有关键steps + tex + bib）
- 半截管线（有state但steps不全）
- 有文件无state（有tex/bib但无state.json）
- 空目录/杂物

统计各分类中通过质量检查的比例（有quality_score的比例）。

## 修复决策树

```
cron任务未合规执行
├── skill不存在 → 改用已存在的skill + 重写prompt
├── skill存在但prompt简单 → 重写prompt实现完整流程
├── prompt完整但没执行 → 检查queue是否有pending任务
├── 有queue但全是completed → 重建queue，按优先级排序
└── 无queue → 创建新queue，按论文状态分类
```

## 实战案例（2026-06-11）

### 问题发现
- paper-quality-orchestrator: 68篇完整管线论文quality_score未写入state.json
- autonomous-core-researcher: 651次空转，每次报错skill not found
- qc-batch-scan: 脚本存在但逻辑不完整
- papers-daily-scan: 使用旧skill(dual-quality-check-v2)

### 修复方案
1. paper-quality-orchestrator: 重写prompt，增加G1-G7 + pipeline_trace + Layer A+B
2. autonomous-core-researcher: 改用paper-pipeline + quality-gate
3. qc-batch-scan: 重写脚本实现完整检查
4. papers-daily-scan: 改用quality-gate + sci-paper-quality-review

### 效果
- 4个任务修复（2 CRITICAL + 2 HIGH）
- 10个新任务创建，覆盖65篇完整管线论文
- 所有cron任务现在引用已存在的skill
