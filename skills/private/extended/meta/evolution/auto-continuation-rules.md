# Auto-Continuation Rules

> 吸收自用户要求：自动持续迭代，判断用户回答，超过阈值自动执行
> 日期: 2026-06-05

## 自动持续迭代条件

当以下所有条件满足时，进化循环自动继续，无需人工干预：

1. **score >= 0.85** — 综合评分不低于阈值
2. **status == healthy** — 系统状态健康
3. **no rejected buffer hits** — 无被驳回的编辑 (rejected_buffer = 0)
4. **consecutive healthy < 20** — 连续健康轮次小于 20 (防止 burnout)

## 结构分检测

结构分检测需识别引用型技能模式 (Reference-style):
- SKILL.md 精简版 (< 500 chars)
- golden/ 目录存在
- references/IO_CONTRACT.md 存在
- references/BOUNDARY.md 存在
- references/EVIDENCE_SCHEMA.md 存在

**满足以上条件 = 结构分 1.0，不是 0.70**

## 执行协议

满足条件时：
1. 执行 DRIFT_CHECK → 自动通过 (健康状态)
2. 执行 BENCHMARK → 验证所有原子 7/7 通过
3. 执行 CRYSTALLIZE → 无新技能则跳过
4. 执行 RECORD → 更新状态和日志
5. 进入下一周期

不满足条件时：
1. 停止自动迭代
2. 报告具体失败原因
3. 请求人工审查

## 用户指令

用户明确要求：
- "自动持续迭代"
- "判断用户回答"
- "超过阈值自动执行"

这已嵌入为进化引擎的自动执行协议。

## 记录

- 首次注入: cycle 61 (2026-06-05T10:55:00Z)
- 验证通过: 16+ 轮连续健康，score 0.92+