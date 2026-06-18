# Pipeline Trace — 步骤执行追踪机制

## 核心原理（文言）

> **行必有迹，步必有录。**
> 不凭记忆而凭记录，不靠感觉而靠日志。
> 每步有状态，每门有闸证。

## 问题

当前流程中：我做什么不做什么，完全靠LLM会话记忆决定。
- 上一步真的做了吗？→ 可能在另一轮对话中
- 这一步的产出在哪里？→ 可能忘了存
- 门检通过了吗？→ 可能只是口头说"通过"

## 解决方案：pipeline-trace.json

每个管线项目（如Synthos论文）维护一个 `pipeline-trace.json` 文件：

```json
{
  "project": "Synthos论文",
  "version": "1.0",
  "started_at": "2026-05-22T13:00:00",
  "steps": [
    {
      "step_id": "P-1.1",
      "name": "逐问文献检索",
      "status": "completed",
      "output": "outputs/domain-map.md",
      "outputs": ["outputs/domain-map.md"],
      "gate": {
        "status": "passed",
        "criterion": "≥5篇不同源去重结果",
        "evidence": "15系统(本地吸收7+外部8)"
      },
      "started_at": "2026-05-22T13:00:00",
      "completed_at": "2026-05-22T13:30:00",
      "duration_min": 30,
      "notes": "OpenAlex串行+S2+本地吸收"
    },
    {
      "step_id": "P-1.2",
      "name": "研究空白定位",
      "status": "completed",
      "output": "outputs/gap-analysis.md",
      "gate": {
        "status": "passed",
        "criterion": "CARS Move2: 双源交叉验证",
        "evidence": "5盲区各有2+来源佐证"
      }
    },
    {
      "step_id": "P3",
      "name": "核心论文下载",
      "status": "pending",
      "output": null,
      "gate": {
        "status": "blocked",
        "criterion": "≥5篇核心PDF下载成功",
        "evidence": null
      }
    }
  ],
  "blockers": ["P3: arXiv服务不可用"],
  "quality_status": "in_progress",
  "last_updated": "2026-05-22T13:30:00"
}
```

## 每步执行前的检查

执行 Step N 前：
```
1. 读取 pipeline-trace.json
2. 检查 Step N-1 的 gate.status == "passed"？
   ├── ✅ 是 → 执行 Step N
   └── ❌ 否 → 必须先完成 Step N-1，不可跳步
3. 检查 Step N 的 status == "pending"（未做过）？
   ├── ✅ 是 → 执行
   └── ❌ 已做过 → 检查是否要重做（如质量不合格）
```

## 门检自动化

每一步的Gate都自动检查：

| Step | Gate Criterion | 自动检查方式 |
|:-----|:---------------|:------------|
| P-1.1 | ≥5篇去重结果 | 统计搜索结果 |
| P-1.2 | CARS Move2: 双源交叉 | 每个Gap检查是否有2+来源 |
| P-1.3 | 图尔敏: 可证伪条件≥3条 | 检查假设格式 |
| P3 | ≥5篇PDF成功下载 | 统计outputs/pdf/文件数 |
| P2 | LaTeX编译通过 | pdflatex paper.tex |
| P4 | 7维评审avg≥0.85 | 运行sci-paper-quality-review |

## 使用方式

```bash
# 初始化
echo '{"project":"Synthos", "version":"1.0", "steps":[], "started_at":""}' > pipeline-trace.json

# 每步完成后更新
python3 -c "
import json
with open('pipeline-trace.json') as f: trace = json.load(f)
trace['steps'].append({
    'step_id': 'P-1.1',
    'name': '逐问文献检索',
    'status': 'completed',
    'output': 'outputs/domain-map.md',
    'gate': {'status': 'passed', 'evidence': '15 systems'}
})
trace['last_updated'] = '2026-05-22T13:30:00'
with open('pipeline-trace.json', 'w') as f: json.dump(trace, f, indent=2)
"

# 检查状态
python3 -c "
import json
with open('pipeline-trace.json') as f: trace = json.load(f)
for s in trace['steps']:
    icon = '✅' if s['gate']['status']=='passed' else '🔴' if s['gate']['status']=='blocked' else '🟡'
    print(f\"  {icon} {s['step_id']}: {s['name']} ({s['status']})\")
print(f\"Blockers: {trace.get('blockers', [])}\")
"
```
