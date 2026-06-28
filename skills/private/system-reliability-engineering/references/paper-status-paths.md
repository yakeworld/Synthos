# 论文管线路径与状态文件

## 关键路径

论文status.json不在 `outputs/papers/<paper>/status.json`，而在:

```
outputs/papers/<paper-name>/07-quality/status.json
```

## 读取示例

```python
import json, os

PAPERS_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers"

paper_dirs = [d for d in os.listdir(PAPERS_DIR) 
              if os.path.isdir(os.path.join(PAPERS_DIR, d)) 
              and not d.startswith('_')]

for d in paper_dirs:
    sf = os.path.join(PAPERS_DIR, d, '07-quality', 'status.json')
    if os.path.exists(sf):
        with open(sf) as f:
            s = json.load(f)
        qg = s.get('quality_gates', {})
        overall = qg.get('overall', 'not_started')
        # 'passed' = 通过G7
        # 'in_progress' = G1-G7流程中
        # 'failed' = 某门失败
        # 'not_started' = 未启动
```

## status.json 典型内容

```json
{
  "paper_name": "02-corneal-tension-ODE",
  "stage": "pre-gate",
  "status": "pending_review",
  "quality_score": 0.0,
  "quality_gate": "not_started",
  "quality_gates": {
    "g1_acq": false,
    "g2_ext": true,
    "g3_asc": false,
    "g4_hyp": false,
    "g5_arg": true,
    "g6_ver": false,
    "g7_latex": false,
    "overall": "in_progress"
  }
}
```

## 常见错误

- 在 `outputs/papers/<paper>/status.json` 查找 → 找不到
- 用 `s.get('gates', {})` 读取 → gates字段名是 `quality_gates`
- 用 `s.get('G7', {})` 查通过状态 → 应该查 `quality_gates.overall == 'passed'`

## 完整论文目录结构

```
outputs/papers/<paper-name>/
  01-manuscript/      # 论文正文
  06-references/      # 参考文献
  07-quality/         # 质量检查
    status.json       # ← 状态文件在这里
  paper.tex           # LaTeX源文件
  references.bib      # BibTeX
```