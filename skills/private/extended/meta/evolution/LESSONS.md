# Synthos 教训存储格式

> 吸收自 AutoResearchClaw `evolution.py` (LessonEntry + EvolutionStore)

## 文件位置

`outputs/evolution/lessons.jsonl` — JSON Lines 格式，每行一个教训对象。

## 教训格式

```json
{
  "atom": "knowledge-acquisition",
  "severity": "error|warning|info",
  "category": "api|structural|benchmark|absorption",
  "issue": "人类可读的问题描述",
  "details": "具体的技术细节（API URL、分数、行号等）",
  "timestamp": "2026-05-11T06:00:00Z"
}
```

## 字段说明

| 字段 | 必填 | 可选值 | 说明 |
|------|------|--------|------|
| atom | 是 | 任意原子名或"system" | 问题出在哪个原子 |
| severity | 是 | error/warning/info | 严重程度 |
| category | 是 | api/structural/benchmark/absorption | 问题类别 |
| issue | 是 | 自由文本 | 简短描述 |
| details | 否 | 自由文本 | 补充信息 |
| timestamp | 是 | ISO 8601 | 教训创建时间 |

## 严重程度规则

| severity | 触发条件 | 衰减期 |
|----------|---------|--------|
| error | BENCHMARK失败 / 结构分<0.5 | 30天 |
| warning | API 429/403 / 结构分下降0.05-0.1 / partial pass | 14天 |
| info | 结构分下降<0.05 / 单次API降级 | 7天 |

## 读取方式

```
tail -20 outputs/evolution/lessons.jsonl
```

每次 LESSONS 步骤读取最后20条，按atom过滤后注入BENCHMARK。

## 写入方式

```
echo '{"atom":"...","severity":"...","category":"...","issue":"...","timestamp":"..."}' >> outputs/evolution/lessons.jsonl
```

追加模式，不修改已有条目。

## 清理策略

- 超过30天的 error 教训自动不再注入（但保留在文件中）
- 超过14天的 warning 教训自动不再注入
- 超过7天的 info 教训自动不再注入
- 文件体积超过1MB时，保留最近100条，删除旧的
