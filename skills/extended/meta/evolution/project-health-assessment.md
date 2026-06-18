# 手动项目健康评估 (Project Health Assessment)

> 被吸收自 `project-health-assessment` 技能。提供一种手动、全面的项目健康评估方法论，作为进化引擎自动 PROBE/BENCHMARK/DIAGNOSE 的补充视角。

## 评估步骤

### 1. 获取项目骨架
```bash
ls -la <project_root>/
ls -la <project_root>/skills/
ls -la <project_root>/outputs/
```
查看 README.md 或 README_CN.md 了解定位和架构。

### 2. 核心状态文件
读取: `evolution-state.json`, `evolution-log.md`, `CONSTITUTION.md`

| 字段 | 健康信号 | 警告信号 |
|:-----|:---------|:---------|
| version | 语义化版本号 | 无版本或陈旧 |
| architecture | 清晰架构描述 | 模糊或矛盾 |
| mode | ACTUAL / PRODUCTION | TEST / DEMO 过期 |
| evolution_count | 持续增长 | 长时间无变化 |
| quality_metrics | stable + benchmark_pass | degraded 原子 |
| last_updated | 近期 | 超过2周 |

### 3. Git 健康状况
```bash
git log --oneline -15
git status --short
git remote -v
```
健康信号：活跃、语义化 commit message、无大量未跟踪文件、远程正确。

### 4. 技能库完整性
- 每个 SKILL.md 有 frontmatter (name, description, metadata, allowed-tools)
- 每个核心原子有 references/ 和 golden/
- skill_registry.json 和 skill_tree.json 同步

评分：全部完整=1.0, 部分扩展缺少=0.80-0.95, 核心原子缺少=0.50-0.79

### 5. 自动化健康度
```bash
cronjob action=list
```
检查: cron 启用? 最后运行在24h内? workdir 指向项目根?

### 6. 竞争/任务就绪度
- 检查竞赛材料/或 docs/ 下的交付物
- 核对 deadline 是否临近

### 7. 风险事件分析
- API 退化（S2 429→OpenAlex 备用有效?）
- 结构修复记录
- 原子吸收/合并
- 外部依赖变更

### 8. 综合评分 (100分制)
| 维度 | 说明 |
|:-----|:-----|
| 架构质量 | 设计清晰度、0 Python、宪法约束力 |
| 进化健康度 | 连续健康轮次、综合评分趋势 |
| 技能完整性 | references/golden 覆盖率 |
| 文档完备性 | README、架构图、设计文档 |
| 交付就绪度 | 竞赛/任务材料完备性 |
| 代码规范 | Git hygiene、CI/CD、License |

## 输出格式
使用表格 + 标记: ✅ 健康, 🟡 有风险, 🔴 严重问题
避免大段文字，优先综合评分表汇总。

## 已知陷阱
1. evolution-state.json 时间戳可能超前 (手动测试)
2. 文件移动 (docs/→竞赛材料/) 可能 git 跟踪断裂
3. 进化计数可能=轮次×2 (奇偶各计一次)
4. cronjob 状态检查 Hermes cron，非系统 crontab

---
*Absorbed from `project-health-assessment` skill (v1.0, 2026-05-13).*
