# EVIDENCE_SCHEMA.md — healthcare-dataset-discovery

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `skill_execution` | 本原子执行时产生执行结果 |
| `input_validation` | 输入数据经校验后产生节点 |
| `output_result` | 本原子输出结果时产生节点 |
| `error_state` | 执行异常或失败时产生标记节点 |
| `api_response` | 调用外部API时产生节点，记录请求/响应 |

## 节点结构

```json
{
  "source_type": "skill_execution|input_validation|output_result|error_state|api_response",
  "source_ref": "<skill_name>",
  "skill_id": "healthcare-dataset-discovery",
  "skill_type": "skill",
  "fetch_time": "<ISO>",
  "note": "Execution result from healthcare-dataset-discovery skill"
}
```

## 传递规则

本原子的 evidence_chain 是执行结果的审计追踪。每个结果节点的 source 字段指向具体的技能名称和输入数据。下游需要本原子结果的原子，在此基础上追加新节点。
