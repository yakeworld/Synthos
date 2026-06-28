---
name: observability-system
description: "系统可观测性 — 指标收集、日志分析、链路追踪、仪表盘。为Synthos系统建立完整的可观测性体系。"
version: 1.0.0
allowed-tools:
- terminal
- execute_code
- browser
- cronjob
- skill_manage
- read_file
- write_file
- send_message
metadata:
  synthos:
    version: 1.0.0
    priority: P1
    atom_type: skill
    author: Synthos
    description: "系统可观测性 — 指标收集、日志分析、链路追踪、仪表盘"
    signature: 'observability -> metrics + logs + traces + dashboards'
    related_skills: ["system-reliability-engineering", "capacity-planning", "incident-response"]
triggers:
  - 需要建立监控体系
  - 需要日志分析或链路追踪
  - 需要仪表盘或报告
  - 告警规则需要制定
  - 用户要求评估系统可观测性

---

# observability-system

> 系统可观测性方法论，为Synthos系统建立完整的指标、日志、追踪和仪表盘体系。

## 触发条件

- 需要建立监控体系
- 需要日志分析或链路追踪
- 需要仪表盘或报告
- 告警规则需要制定
- 用户要求评估系统可观测性

## 执行步骤

1. **建立指标体系** — 三层指标:
   - **系统指标**: CPU/Memory/Disk/Network使用率、vLLM响应时间、Cron执行时间、技能加载时间
   - **业务指标**: 论文产出率(篇/月)、知识增长(节点/月)、技能复用率、质量通过率
   - **质量指标**: 可用性(99.9%)、成功率(95%)、MTTR(<30min)、MTBF(>30天)

2. **配置日志收集** — 结构化日志规范:
   - JSON格式: `{"timestamp","level","service","event","duration_ms","status","metadata"}`
   - 日志级别: DEBUG/INFO/WARN/ERROR/FATAL
   - 保留策略: 热日志7天、温日志30天、冷日志90天
   - Cron日志: `~/.hermes/cron/output/<job_id>/<date>_time.md`
   - 技能日志: 技能执行输出
   - 系统日志: 系统运行状态

3. **实现链路追踪** — 分布式追踪:
   - trace_id: 唯一标识整个调用链
   - span_id: 唯一标识单个操作
   - 追踪范围: Cron任务、技能加载、论文生成、知识图谱更新
   - 记录: 开始时间、结束时间、状态、错误信息

4. **设置告警规则** — 分级告警:
   - **P1告警**: CPU>90%、内存>85%、磁盘>90%、错误率>10%、成功率<90%
   - **P2告警**: CPU>80%、内存>75%、磁盘>80%、错误率>5%、成功率<95%
   - 告警必须关联行动: 收到告警后必须有明确操作

5. **建立仪表盘** — 可视化展示:
   - 资源面板: CPU/Memory/Disk/Network趋势图
   - 性能面板: 响应时间/吞吐量/错误率趋势图
   - 业务面板: 论文数量/质量评分/知识增长趋势图
   - 质量面板: 可用性/可靠性/错误预算趋势图

6. **生成报告** — 自动化+手动:
   - 日报: 系统运行状态、任务统计、错误告警
   - 周报: 趋势分析、瓶颈识别、容量余量
   - 月报: 容量规划、成本分析、改进建议

## Pitfalls

- **指标噪音**: 不是所有指标都有价值。遵循"每个指标必须关联决策"原则——如果一个指标不能触发任何行动，它就是噪音。初始只收集3-5个核心指标，逐步增加。
- **告警疲劳**: 收到太多告警会导致忽略所有告警。告警阈值要合理，不要过敏感。一个告警收到后必须有人响应或自动处理，否则这个告警就是噪音。
- **日志过度记录**: 不是所有操作都需要日志。DEBUG级别用于开发，INFO用于关键操作，ERROR用于异常。避免记录所有HTTP请求到INFO级别。
- **追踪开销**: 分布式追踪有性能开销。不要在关键路径上追踪每个微操作。只追踪有意义的调用链(跨服务/跨模块的调用)。

## 参考

- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- OpenTelemetry: https://opentelemetry.io/docs/

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
