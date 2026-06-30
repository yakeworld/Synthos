---
name: skill-enhanced-llm
description: Skill-Enhanced LLM Reasoning methodology — skill hierarchy, dynamic selection, skill chain orchestration, quality assessment
metadata:
  synthos:
    priority: P0
    atom_type: class-level
    description: "Skill-Enhanced LLM Reasoning方法论 — 技能层级化、动态选择、技能链编排、质量评估体系"
signature: "skill-enhanced-llm -> processed_result"
---

version: 1.0.0

# Skill-Enhanced LLM Reasoning — 技能化架构方法论

> **文以验法，技乃所产。** 技能不是静态资源，而是需要数据驱动、自动进化、可组合的有机体。

## 核心哲学

**LLM的价值不在于它本身多聪明，而在于它能多好地选择和编排技能。**

传统做法：把LLM当搜索引擎，每次从头推理。
Skill-Enhanced做法：把LLM当调度器，从预定义技能库中选择最优组合。

## 一、技能层级化架构

### 层级定义

```
Level 1: 基础技能 (Atomic)
  - 不可再分的最小功能单元
  - 例如: 数据解析、API调用、数学计算、PDF提取

Level 2: 复合技能 (Composed)
  - 由2+个基础技能组合
  - 例如: 数据清洗→特征提取→模型预测
  - 例如: PDF下载→文本提取→知识卡片生成

Level 3: 高级技能 (Orchestrated)
  - 由复合技能组合，支持复杂推理
  - 例如: 论文管线全流程、实验审计闭环
```

### 层级化原则

1. **单一职责**: 每个基础技能只做一件事
2. **明确接口**: 技能的输入输出必须标准化
3. **可测试性**: 每个技能必须有golden test
4. **独立部署**: 层级之间松耦合，可独立更新

### 现有Synthos技能层级化建议

| 当前状态 | 建议层级 | 示例 |
|---------|---------|------|
| 207个扁平技能 | 重新归类为3层 | skill-quality-check → Level 1 |
| 部分技能可组合 | 创建复合技能 | paper-citation-health + experiment → Level 2 |
| 复杂流程 | 抽象为高级技能 | 论文管线、实验审计 → Level 3 |

## 二、动态技能选择

### LLM作为调度器

当用户提交任务时，LLM执行以下决策链：

```
用户请求
  ↓
1. 任务分类 (分类到哪个领域)
  ↓
2. 技能检索 (从该领域找最匹配的技能)
  ↓
3. 技能选择 (选1个或组合多个)
  ↓
4. 调用执行
  ↓
5. 结果验证
  ↓
6. 反馈记录 (用于技能使用率统计)
```

### 选择策略

**策略1: 匹配度优先**
- 语义匹配度最高的技能
- 适用于：任务描述清晰、有明确技能对应

**策略2: 使用率优先**
- 最近使用频率最高的技能
- 适用于：重复性任务

**策略3: 成功率优先**
- 历史成功率最高的技能
- 适用于：关键任务，需要高可靠性

**策略4: 组合最优**
- 多个技能组合后效果最佳
- 适用于：复杂任务，需要多技能协同

### 实现建议

```python
# 伪代码
def select_skill(task_description, user_context):
    # 1. 语义检索
    candidates = semantic_search(task_description, skill_library)
    
    # 2. 过滤不可用的技能
    candidates = filter_available(candidates, system_context)
    
    # 3. 多维度评分
    scores = {}
    for skill in candidates:
        scores[skill] = (
            0.3 * semantic_match(task, skill) +
            0.3 * usage_rate(skill) +
            0.2 * success_rate(skill) +
            0.2 * coverage(skill, task)
        )
    
    # 4. 选择最高分
    return max(scores, key=scores.get)
```

## 三、技能链编排

### 技能链定义

技能链 = 有序的技能序列，每个技能的输出是下一个技能的输入。

```
[技能A: 数据下载]
    ↓
[技能B: 数据清洗]
    ↓
[技能C: 特征提取]
    ↓
[技能D: 模型训练]
    ↓
[技能E: 结果验证]
```

### 编排引擎设计要素

1. **依赖管理**: 技能之间的输入输出依赖关系
2. **并行执行**: 无依赖的技能可以并行
3. **错误处理**: 某个技能失败时的回退或重试机制
4. **状态传递**: 技能之间共享中间状态
5. **可观测性**: 执行过程的实时监控和日志

### 错误处理策略

| 场景 | 策略 |
|------|------|
| 技能A失败 | 重试1次，仍失败则通知用户 |
| 技能B失败(非关键) | 跳过，继续执行后续技能 |
| 技能C失败(关键) | 回滚到最近成功状态，通知用户 |
| 所有备选失败 | 降级方案：LLM直接生成 |

## 四、技能质量评估体系

### 四维评估指标

| 维度 | 指标 | 计算方法 | 目标值 |
|------|------|---------|--------|
| 准确率 | skill_accuracy | 成功执行次数 / 总执行次数 | ≥ 90% |
| 效率 | skill_latency | 平均执行时间(秒) | ≤ 30s |
| 鲁棒性 | skill_stability | 标准差 / 均值(CV值) | ≤ 0.15 |
| 覆盖度 | skill_coverage | 覆盖任务类型数 / 总任务类型数 | ≥ 80% |

### 技能使用率监控

```
每周统计:
  1. 每个技能的调用次数
  2. 每个技能的成功率
  3. 每个技能的平均耗时
  4. 新技能发现需求(用户请求但无对应技能)
  
每月分析:
  1. 使用率TOP10技能 (重点维护)
  2. 使用率BOTTOM10技能 (考虑淘汰或合并)
  3. 新需求聚类 (需要创建新技能)
  4. 技能层级关系变更 (重新分层)
```

### 技能生命周期

```
创建 → 测试 → 上线 → 监控 → 优化 → 淘汰
  ↑                              ↓
  └──────── 迭代优化 ←───────────┘
```

| 阶段 | 动作 | 标准 |
|------|------|------|
| 创建 | 编写SKILL.md + 测试用例 | 思想密度≥3条核心原则 |
| 测试 | 运行golden test | 全部通过 |
| 上线 | 发布到技能库 | 版本号+changelog |
| 监控 | 收集使用数据 | 每周更新 |
| 优化 | 根据数据迭代 | 每月1次 |
| 淘汰 | 标记deprecated | 使用率<5%持续3个月 |

## 五、技能自动发现与进化

### 自动发现流程

```
1. 收集用户请求日志
  ↓
2. 聚类分析 (发现重复性请求模式)
  ↓
3. 匹配现有技能 (是否有对应技能)
  ↓
4. 生成技能草案 (LLM根据模式生成)
  ↓
5. 人工审核 (用户确认)
  ↓
6. 上线测试
  ↓
7. 正式纳入技能库
```

### 与Synthos进化循环对接

将技能进化作为evolution cycle的一部分：

```
evolution-cycle:
  - 常规维度: structural, knowledge, absorption, quality, reliability
  - 新增维度: skill_efficiency (技能链编排效率)
  - 技能自动发现: 每次evolution cycle检查是否需要新技能
  - 技能淘汰: 每次evolution cycle标记低使用率技能
```

## 六、与现有Synthos技能的对接

### 立即可以做的

1. **技能使用率统计**: 从cron run记录中提取每个技能的使用频率
2. **技能层级化**: 将现有207个技能按"原子→复合→高级"重新分类
3. **技能质量评估**: 为每个技能计算准确率、效率、鲁棒性、覆盖度

### 中期改进

4. **技能链编排**: 设计多技能串联的编排引擎
5. **动态选择**: LLM根据任务描述自动选择最优技能
6. **自动发现**: 从用户请求中自动发现新技能需求

### 长期愿景

7. **技能市场**: 技能可以共享、复用、评分
8. **技能进化**: LLM自动优化技能实现
9. **技能生态**: 社区驱动的技能共享和协作

## 七、验证步骤

1. **统计现有技能使用率**:
   ```bash
   # 技能文件统计
   find /home/yakeworld/.hermes/skills -name "SKILL.md" | wc -l
   
   # 按层级统计
   find /home/yakeworld/.hermes/skills -maxdepth 2 -name "SKILL.md" | wc -l
   find /home/yakeworld/.hermes/skills -maxdepth 3 -name "SKILL.md" | wc -l
   
   # 提取每个技能的名称、描述、大小
   for f in $(find /home/yakeworld/.hermes/skills -name "SKILL.md"); do
       name=$(grep -m1 "name:" "$f" | sed 's/name: *//' | awk '{print $1}')
       size=$(stat -c%s "$f")
       echo "$name ($size B)"
   done
   ```

2. **从cron输出提取运行数据**:
   ```bash
   # 统计每个任务ID的运行次数
   for dir in /home/yakeworld/.hermes/cron.output/*/; do
       name=$(grep -m1 "Cron Job:" "$dir"*.md 2>/dev/null | sed 's/.*Cron Job: //')
       runs=$(ls -1 "$dir"*.md 2>/dev/null | wc -l)
       echo "$name: $runs 次运行"
   done
   ```

3. **识别未映射任务**:
   ```bash
   # 找出输出目录存在但不在jobs.json中的任务
   # 这些是已删除/重命名但仍有输出的任务
   for dir in /home/yakeworld/.hermes/cron.output/*/; do
       name=$(grep -m1 "Cron Job:" "$dir"*.md 2>/dev/null | sed 's/.*Cron Job: //')
       echo "$name"
   done
   ```

4. **识别高频技能**:
   - 使用率TOP10: 从cron输出统计运行次数
   - 使用率BOTTOM10: 使用率<5%持续3个月 → 淘汰

5. **建立质量基线**:
   ```python
   skill_efficiency = {
       "total_skills_in_repo": 191,     # evolution state
       "total_skills_in_hermes": 27,    # hermes/skills目录
       "active_cron_tasks": 15,         # jobs.json中的数量
       "high_frequency_tasks": 3,       # 运行>100次
       "low_frequency_tasks": 8,        # 运行<10次
       "orphaned_output_dirs": 6,       # 未映射但有输出的目录
       "skill_utilization_rate": 0.27,  # 27/191
       "cron_activity_rate": 0.93,      # 活跃任务比例
   }
   ```

## 八、Pitfalls
- **空壳技能(<200B)**: 200-1000B为小文件，1-5KB为中等，>5KB为完整
- **实际采集数据**: 2026-06-29首次完整采集 — 27个hermes技能(0个L1原子、3个L2复合、5个L3高级、19个未定级)，21个cron任务(15活跃、6已归档)，1352次运行。Top 2: gpu-heartbeat(1028次)、paper-quality-orchestrator(173次)。skill-efficiency 0.65(new evolution dim)。6个未映射目录清理释放1032KB。
- **过度层级化**: 层级不是越多越好，2-3层足够
- **技能膨胀**: 不要为每个小任务创建技能，先尝试组合现有技能
- **缺乏测试**: 没有golden test的技能不可上线
- **静态管理**: 技能需要持续监控和优化，不是一劳永逸
- **LLM依赖过强**: 技能执行不依赖LLM，LLM只是调度器
- **忽略使用率数据**: 技能好不好用，数据说了算，不是感觉
- **技能之间强耦合**: 层级之间要松耦合，避免牵一发而动全身
- **未映射cron输出**: 已删除/重命名的任务在cron.output/目录留下残留，需定期清理
- **UUID目录名**: cron输出目录常以UUID命名(如`1ce1379174ea`)，需要通过文件内容grep提取任务名
- **层级检测依赖描述关键词**: 用描述中的"方法论"/"编排"/"完整"/"管线"判断L3，用"工具"/"CLI"/"API"判断L1
- **空壳技能(<200B)**: 200-1000B为小文件，1-5KB为中等，>5KB为完整
- **实际采集数据**: 2026-06-29首次完整采集 — 27个hermes技能(0个L1原子、3个L2复合、5个L3高级、19个未定级)，21个cron任务(15活跃、6已归档)，1352次运行。Top 2: gpu-heartbeat(1028次)、paper-quality-orchestrator(173次)。skill-efficiency 0.65(new evolution dim)。6个未映射目录清理释放1032KB。
- **过度层级化**: 层级不是越多越好，2-3层足够- **空壳技能(<200B)**: 200-1000B为小文件，1-5KB为中等，>5KB为完整
- **实际采集数据**: 2026-06-29首次完整采集 — 27个hermes技能(0个L1原子、3个L2复合、5个L3高级、19个未定级)，21个cron任务(15活跃、6已归档)，1352次运行。Top 2: gpu-heartbeat(1028次)、paper-quality-orchestrator(173次)。skill-efficiency 0.65(new evolution dim)。6个未映射目录清理释放1032KB。
- **过度层级化**: 层级不是越多越好，2-3层足够
- **技能膨胀**: 不要为每个小任务创建技能，先尝试组合现有技能
- **缺乏测试**: 没有golden test的技能不可上线
- **静态管理**: 技能需要持续监控和优化，不是一劳永逸
- **LLM依赖过强**: 技能执行不依赖LLM，LLM只是调度器
- **忽略使用率数据**: 技能好不好用，数据说了算，不是感觉
- **技能之间强耦合**: 层级之间要松耦合，避免牵一发而动全身

## 九、Golden Test

**输入**: 用户请求"帮我分析这篇论文的引用健康度"
**预期**:
1. LLM选择 `paper-citation-health` 技能
2. 执行PDF下载 → 文本提取 → 引用分析 → 报告生成
3. 输出: 标准化的引用健康报告
4. 记录: 技能使用数据 + 执行时间 + 成功状态

## 十、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.1 | 2026-06-29 | 补充实际运行数据、cron统计命令、未映射目录清理pitfall、层级化关键词检测规则 |
| 1.0.0 | 2026-06-29 | 初始版本: 基于Auto-Skill/SkillWeaver/Skill-MAS/OpenClaw-Skill论文的方法论吸收 |

## 十、参考文件

- `references/skill-usage-data.md` — 首次完整采集的技能使用率数据(27个技能、21个cron任务、1352次运行)
- `references/skill-usage-data-v2.md` — 更新版：含已归档任务、技能库统计、evolution-state.json摘要



# Skill Enhanced Llm

