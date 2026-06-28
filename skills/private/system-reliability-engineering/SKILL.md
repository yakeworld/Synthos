---
name: system-reliability-engineering
description: "系统可靠性工程 — SRE、可观测性、混沌工程、容量规划、事故响应。基于Google SRE方法论，为Synthos系统建立可靠性保障体系。"
version: 2.0.0
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
    priority: P0
    atom_type: parent-skill
    author: Synthos
    description: "父级技能 — 系统可靠性工程 — SRE、可观测性、混沌工程、容量规划、事故响应"
    signature: 'reliability -> SLO + monitoring + chaos + capacity + incident'
    related_skills: ["devops", "cron-system-maintenance", "quality-gate", "incident-response", "capacity-planning", "chaos-engineering", "observability-system", "infrastructure-as-code", "continuous-delivery-pipeline"]
    sub_skills: ["incident-response", "capacity-planning", "chaos-engineering", "observability-system", "infrastructure-as-code", "continuous-delivery-pipeline"]
    description: "父级技能 — 系统可靠性工程。子类: incident-response, capacity-planning, chaos-engineering, observability-system, infrastructure-as-code, continuous-delivery-pipeline"
triggers:
  - 系统可用性低于SLO
  - 需要建立可靠性监控体系
  - Cron连续error需要根因分析
  - 系统资源使用率超过阈值
  - 用户要求评估系统可靠性

---

# system-reliability-engineering

> 基于Google SRE方法论的系统可靠性工程体系，为Synthos智能系统建立工程化可靠性保障。

## 触发条件

- cron job list中任何job `last_status == "error"`且持续≥3次
- 系统可用性低于99.9% SLO
- 用户要求评估系统可靠性或建立监控
- 系统资源使用率超过告警阈值(CPU>80%/内存>75%)
- 进化循环score连续2轮低于0.85

## 执行步骤

1. **建立SLI/SLO/SLA体系** — 定义系统服务质量指标
   - 可用性: cron成功率、技能加载成功率、论文生成成功率
   - 延迟: vLLM响应时间(<100ms P50), Cron执行时间(<60s P50)
   - 准确性: 论文质量评分、引用验证准确率
   - 完整性: 知识图谱连通性(100%)、技能完整性

2. **计算错误预算** — `错误预算 = 1 - SLO目标`
   - P0任务(进化循环): 99.9% SLO → 每月43分钟错误预算
   - P1任务(论文管线): 99% SLO → 每月7小时错误预算
   - P2任务(知识库): 95% SLO → 每月3.6天错误预算
   - 消耗>80%错误预算时触发告警

3. **建立可观测性三支柱**
   - **指标**: 系统指标(CPU/Memory/Disk/Network)、业务指标(论文产出/知识增长/技能复用)、质量指标(可用性/成功率/MTTR/MTBF)
   - **日志**: 结构化日志JSON格式(含timestamp/level/service/event/duration/status/metadata)，保留策略(热7天/温30天/冷90天)
   - **追踪**: 每个cron任务生成trace_id，技能调用链追踪，论文生成流程追踪

4. **实施监控告警**
   - 资源告警: CPU>90%(P1)/CPU>80%(P2), 内存>85%(P1)/>75%(P2), 磁盘>90%(P1)/>80%(P2)
   - 性能告警: 响应时间>1s(P2)/5s(P1), 错误率>5%(P2)/10%(P1)
   - 业务告警: Cron连续失败>3次, 知识图谱连通性<95%, 论文质量评分<0.7

5. **设计混沌实验**
   - 节点故障: 关闭vLLM节点→验证自动路由
   - 技能缺失: 删除关键技能→验证检测和恢复
   - 数据损坏: 损坏图谱文件→验证备份恢复
   - 容量耗尽: 模拟磁盘满/内存耗尽→验证降级行为
   - 实验原则: 假设驱动、渐进式扩展、有终止条件、有回滚机制

6. **容量规划**
   - 基于历史数据: 论文产出增长10%/月、知识增长50节点/月、技能增长5技能/月
   - 容量公式: 所需容量 = 当前使用 × (1 + 增长率) × 安全系数(1.5)
   - 扩展策略: 水平扩展(多vLLM节点/多Cron实例)、垂直扩展(CPU/内存/存储升级)

7. **事故响应流程**
   - 事故分级: P0(完全不可用/15min响应)、P1(核心受损/1hr响应)、P2(非核心受损/4hr响应)、P3(体验问题/24hr响应)
   - 处理步骤: 检测→确认→遏制→恢复→验证→复盘
   - 复盘模板: 无责备文化、关注系统而非个人、时间线重建、根因分析、改进措施

8. **持续改进**
   - 反馈循环: 监控→分析→优化→部署→验证→监控
   - 质量门控: 每次变更经过SRE检查(错误预算/性能指标/容量余量)
   - 定期演练: 月度桌面演练、季度实战演练、年度综合演练

## Pitfalls

- **错误预算计算陷阱**: 不可用时间包含所有SLO违规(不仅是停机)，还包括性能降级和错误率升高。计算时用总时间-合规时间/总时间，不是简单1-SLO。
- **告警疲劳**: 初始告警规则过多会导致告警疲劳。建议从3-5个核心告警开始，逐步增加。告警必须关联行动——收到告警后必须有明确操作。
- **混沌工程风险**: 不要在生产环境直接运行混沌实验。先在开发环境验证，再测试环境，最后预生产。必须有终止条件(错误率>10%时立即停止)和回滚机制。
- **容量规划过时**: 增长率是动态变化的。每季度重新评估一次增长趋势，调整容量模型。不要依赖单次预测。
- **指标噪音**: 不是所有指标都有价值。遵循"每个指标必须关联决策"原则——如果一个指标不能触发任何行动，它就是噪音。
- **MTTR统计偏差**: MTTR=总恢复时间/事故次数，但"恢复"定义不一。统一标准: 从检测到恢复为SLO内。不是"开始处理"，是"服务完全恢复"。
- **错误预算耗尽后的处理**: 错误预算耗尽时不应简单"停止部署"，而是进入分级策略: P0功能暂停部署、P1功能减缓部署、P2功能正常部署。

## 参考

- Google SRE Book: https://sre.google/sre-book/table-of-contents/
- Netflix Chaos Engineering: https://netflix.github.io/chaos/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/
- Observability Triad: https://signoz.io/blog/observability-triad/

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
