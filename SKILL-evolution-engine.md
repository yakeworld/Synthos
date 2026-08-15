# 自主进化引擎

## 架构原则

进化引擎是平台的核心自组织机制。它在无人值守时持续运行，
基于 Synthos 哲学自主决定优化方向。

## 进化循环

1. **评估**：对所有原子执行质量检查
   - trust_score 更新（基于成功率/用户反馈）
   - usage_count 统计（基于实际调用）
   - 错误模式分析

2. **决策**：基于评估结果决定优化方向
   - 低 trust_score 原子 → 触发重新训练/参数优化
   - 高 usage_count 原子 → 优先保障资源
   - 瓶颈原子（高依赖） → 增加冗余/优化

3. **执行**：应用优化
   - 更新 skill.yaml 参数（超时、重试、资源）
   - 优化 fallback 链
   - 添加/移除依赖关系

4. **验证**：检查优化效果
   - 对比优化前后质量指标
   - 记录在 evolution-report.json

## 进化模式

### 分析模式（默认）
只报告分析结果，不实际执行改变。

### 实际模式
实际执行优化改变。通过 `--force` 参数启用。

## dsh 驱动进化 (2026-08-16 新增)

需要 LLM 推理能力的改进任务（语义化 IO_CONTRACT、验证清单生成、引用审计、吸收五维评估）
通过 **dsh headless agent** 隔离执行，由 `skills/extended/dsh-self-evolution` 技能编排：

```
父 Agent: DIAGNOSE → 构造任务 prompt(4要素, ≤15文件) → VERIFY(独立重算) → RECORD
    │
    └─ bash -lc 'dsh --profile headless "<task>"'  →  隔离执行体
```

关键纪律：
- dsh 必须经 `bash -lc` 调用（VLLM 凭据环境变量仅存于登录 shell 环境）
- dsh 不 commit、不改 state/log — 提交由父 Agent 按 commit-scope-check 执行
- 验证独立重算，声称≠实测 记 self_deception_risk（Cycle 186 自欺教训）

## 状态管理

状态存储在 `evolution-state.json`：
- version: 引擎版本
- mode: ANALYSIS | ACTUAL
- last_run: 最后执行时间
- quality_metrics: 各原子质量分数
- evolution_count: 进化轮次
- trust_db: 信任数据库

## 认知偏差检测

引擎定期检查：
- 确认偏误：是否只关注支持性证据
- 选择偏误：检索范围是否过窄
- 过度自信：置信度是否过高
- 逻辑断裂：论证链条是否完整

## Synthos 对齐

- **证伪主义**：主动寻找反证
- **贝叶斯思维**：基于证据更新信任度
- **自由能原理**：最小化预测误差
- **系统思维**：全局优化而非局部最优


## 奥卡姆剃刀原则

- 每个任务必须使用最短原子链
- 路由器自动跳过不必要的原子
- 简单任务只需1-2个原子
- 完整任务可选跳过验证环节
- 绝不强制走6步流程
