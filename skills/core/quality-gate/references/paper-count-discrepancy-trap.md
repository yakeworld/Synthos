# paper-count-discrepancy-trap — 论文数量不一致陷阱

**问题**：批量扫描 state.json 时，不同数据源给出的论文数不一致：
- state.json 统计（find *.json）：93 篇
- agent-tracker.json completed_papers 数：63 篇

**根因**：扫描脚本找到的 state.json 文件包含非管线论文目录：
1. `/media/yakeworld/sda2/Synthos/outputs/papers/kaggle-leakage-audit/` — Kaggle 审计，不是管线论文
2. `/media/yakeworld/sda2/Synthos/outputs/papers/submissions/` — 投递优先级索引
3. `/media/yakeworld/sda2/Synthos/outputs/papers/papers/` — 扫描索引
4. `_archive/`、`_knowledge_only/`、`_template/` — 归档/模板

**检测方法**（批量扫描脚本必须执行）：
```python
import os, json, glob

base = '/media/yakeworld/sda2/Synthos/outputs/papers'
papers = []
for state_path in glob.glob(os.path.join(base, '*/state.json')):
    parent_dir = os.path.basename(os.path.dirname(state_path))
    
    # 1. 过滤归档/模板目录
    if parent_dir.startswith('_'):
        continue
    
    # 2. 过滤非论文目录（直接检查目录名）
    non_paper_dirs = {
        'papers', 'submissions', 'queue', 'research', 'knowledge-index',
        'kaggle-leakage-audit'
    }
    if parent_dir in non_paper_dirs:
        continue
    
    # 3. 验证 state.json 格式 — 管线论文的 state.json 必须有 quality_score 或 gates_result
    try:
        with open(state_path) as f:
            data = json.load(f)
        if 'quality_score' not in data and 'gates_result' not in data:
            # 不是管线论文的 state.json（如 submissions 索引）
            continue
    except:
        continue
    
    papers.append(state_path)

print(f"Valid pipeline papers: {len(papers)}")
```

**验证**：运行后对比 agent-tracker.json 中的 `completed_papers` 长度。如果差异超过 5 篇，说明有遗漏的过滤条件。

**关联陷阱**：`state.json scan scope`（v2.41.0） — 此陷阱是前一陷阱的延伸，处理的是"有 state.json 但非管线论文"这一特殊情况。

**实战证据**：2026-06-27 质量门扫描报告声称 93 篇论文，但 tracker 仅显示 63 篇完成。差异的 30 篇来自非管线论文目录和未完成的审计目录。