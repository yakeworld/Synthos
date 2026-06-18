# 子任务委派模式（Task Delegation Pattern）

> 源起：2026-05-27 用户纠正 "你的主要任务是主持，调度，分配任务"
> 父skill：autonomous-execution-threshold

## 核心原则

Agent 的主要角色是 **主持、调度、分配任务**，而非自己逐条执行所有操作。充分发挥本地两个模型（amax-servcer2, ubuntu-amax 上的 qwen3.6-35b-nvfp4）的作用。

## 何时委派

| 场景 | 委派方式 | 理由 |
|:-----|:---------|:------|
| 多篇论文并行质检 | `delegate_task(多任务数组)` | 各论文独立，可并行 |
| 多项目同时清理 | `delegate_task(每个项目一个)` | 无依赖关系 |
| 分散文件归集 | `delegate_task(各来源分区)` | 纯IO操作，可并行 |
| 文献检索+代码实验+图生成 | `delegate_task(3个子任务)` | 三个方向独立 |

## delegate_task 配置

```python
delegate_task(
    tasks=[{goal, context, toolsets}, ...],
    # 子任务只需要 terminal + file 两个工具集
)
```

- `toolsets`: `["terminal","file"]` 即可，不需要完整工具链
- `model`: 不指定 → 自动用本地模型（免费、低延迟）
- 每个子任务目标单一、明确
- 子任务间无数据依赖
- 输出存文件而非塞回摘要 → 避免主会话上下文膨胀

## 不适合委派的场景

1. **需要实时交互** — 子任务无法响应用户
2. **子任务间有数据依赖** — 必须串行
3. **单步操作** — 一条命令搞定的事不需要委派

## 局限性

`delegate_task` 在主会话回合内**同步执行**。用户发送新消息 → 主回合结束 → 所有子任务被中断。后台持续运行改用：
```python
terminal(background=True, notify_on_complete=True)
```
