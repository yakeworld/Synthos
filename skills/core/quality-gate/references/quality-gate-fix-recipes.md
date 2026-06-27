# state.json 数据录入错误修复配方

## 错误模式与修复

### 1. 小数点错误
**症状**: quality_score = 0.935（应为 93.5）
**原因**: pipeline 将百分比除以100后未乘回
**修复**:
```python
import json
with open('state.json') as f: d = json.load(f)
# 如果分数明显是 0-1 范围但实际应为 0-100
if isinstance(d['quality_score'], float) and 0 < d['quality_score'] < 1:
    d['quality_score'] = round(d['quality_score'] * 100, 1)
# 或者从 gates_result 取正确的分数
if 'gates_result' in d and isinstance(d['gates_result'], dict):
    gr = d['gates_result']
    if isinstance(gr.get('quality_score'), (int, float)):
        d['quality_score'] = gr['quality_score']
with open('state.json', 'w') as f:
    json.dump(d, f, indent=2)
```

### 2. top-level gate 未更新
**症状**: gate_status = PASS, 但 gates_result.hard_fails > 0
**原因**: 旧版 pipeline 自报 PASS，新版 G7 审计发现硬失败，gate_status 未同步
**修复**:
```python
with open('state.json') as f: d = json.load(f)
gr = d.get('gates_result', {})
if gr.get('hard_fails', 0) > 0:
    d['gate_status'] = 'HARD_FAIL'
elif gr.get('soft_fails', 0) > 0:
    d['gate_status'] = 'SOFT_FAIL'
d['last_updated'] = '2026-06-25T05:00:00+08:00'
with open('state.json', 'w') as f: json.dump(d, f, indent=2)
```

### 3. 内部分数不一致
**症状**: quality_score=85, gates_result.quality_score=20，差异>65分
**原因**: 不同 pipeline 版本产生的分数不一致
**修复**:
- 以 `gates_result.quality_score` 为准（独立审计）
- 更新 top-level `quality_score` 与之同步
- 更新 `gate_timestamp` 标记修改时间

### 4. 低分论文显示 PASS
**症状**: quality_score=68（低于及格线75），gate_status=PASS
**原因**: 低分但未被标记为不通过
**修复**:
- 检查 `gates_result.hard_fails` 和 `gates_result.soft_fails`
- 如果有 hard_fails，gate_status 应改为 HARD_FAIL
- 如果只有 soft_fails，gate_status 应改为 SOFT_FAIL
- 如果 gates_result 全为 PASS 但 top_score 低，保持 PASS 但记录异常
