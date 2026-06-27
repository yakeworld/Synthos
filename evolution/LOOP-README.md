# 自主进化循环 (Evolution Loop)

## 架构

```
AUDIT → ANALYZE → FIX → VERIFY → RECORD
  ↑___________________________________↓
        循环持续进行
```

## 核心组件

| 文件 | 功能 |
|------|------|
| `evolution-loop.py` | 主循环脚本 — 扫描、分析、修复、验证 |
| `skills/check_skill.py` | 质量检查引擎 v2 — 实际执行技能检查 |
| `evolution/evolution-loop-cron.sh` | cron 定时任务脚本 |
| `evolution-state.json` | 进化状态 — cycle, dimensions, scores |
| `evolution-log.md` | 进化日志 — 每次循环的摘要 |
| `evolution-report-cycle-N.json` | 单轮完整报告 |

## 用法

### 快速扫描（推荐日常使用）

```bash
# 扫描核心认知原子（~1s）
python3 evolution-loop.py --scan --subset core

# 扫描扩展技能（~8s）
python3 evolution-loop.py --scan --subset extended

# 扫描私人技能（~3s）
python3 evolution-loop.py --scan --subset private

# 全部扫描（~30s，慢）
python3 evolution-loop.py --scan --subset all
```

### 分析与修复

```bash
# 仅分析问题（不修改文件）
python3 evolution-loop.py --fix --subset core

# 分析 + 尝试自动修复
python3 evolution-loop.py --fix --subset extended
```

### cron 定时任务

```bash
# 每4小时运行完整循环
0 */4 * * * /media/yakeworld/sda2/Synthos/evolution/evolution-loop-cron.sh
```

## 输出格式

扫描后生成：
1. **终端报告** — Markdown 格式，包含总览、P0/P1问题、最低分技能
2. **JSON报告** — `evolution-report-cycle-N.json`，完整数据
3. **状态更新** — `evolution-state.json` 中的 dimensions 和 cycles
4. **日志追加** — `evolution-log.md`

## 质量维度

| 维度 | 含义 | 目标 |
|------|------|------|
| structural | 技能结构完整性 | ≥0.95 |
| benchmark | 引用/签名完整性 | =1.0 |
| coverage | 健康技能比例 | ≥0.90 |
| optimize | 优化进度 | ≥0.80 |
| absorption | 技能吸收完成度 | ≥0.85 |
| constitutional | 宪法对齐度 | =1.0 |

## 自动化流程

```
1. run_check_skill.py 扫描所有技能
2. 收集分数、问题、建议
3. 按严重度排序: P0 > P1 > P2
4. P0: 紧急修复（引用、架构）
5. P1: 建议修复（模式、入口、版本）
6. P2: 可选优化（边界、案例）
7. 记录进化日志
8. 更新 evolution-state.json
9. 生成报告
```
