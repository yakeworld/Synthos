# 百篇级论文管线扫描协议

**适用场景**: 管线中有50+篇论文，需要批量诊断健康状态。

## 核心发现（2026-06-25 实战）

在103篇论文管线中：
- 93篇显示 `gate_status=PASS`
- 但其中 **23篇**（25%）的 `gates_result.hard_fails > 0` 或 `gates_result.quality_score` 显著低于 top-level `quality_score`

**根因**: top-level `gate_status` 由旧版pipeline自报，`gates_result` 是新版G7独立审计结果。旧版gate_status从未被gates_result的低分更新，导致虚假通过。

## 扫描命令

```bash
python3 << 'PYEOF'
import json, os
base = "/media/yakeworld/sda2/Synthos/outputs/papers"
papers = []
for d in sorted(os.listdir(base)):
    dpath = os.path.join(base, d)
    if not os.path.isdir(dpath) or d.startswith('.'): continue
    sj = None
    for c in [os.path.join(dpath, 'state.json'), os.path.join(dpath, '09-manuscript', 'state.json')]:
        if os.path.exists(c): sj = c; break
    if not sj: continue
    try:
        with open(sj) as f: data = json.load(f)
        papers.append({'name': d, 'score': data.get('quality_score'), 'gate': data.get('gate_status'),
                        'step': data.get('current_step'), 'gr_score': data.get('gates_result',{}).get('quality_score'),
                        'gr_hard': data.get('gates_result',{}).get('hard_fails', 0)})
    except: pass

from collections import Counter
gates = Counter(p['gate'] for p in papers if p['gate'])
print(f"gate_status: {dict(gates)}")

false_pass = [p for p in papers if p['gate'] == 'PASS' and p['gr_hard'] > 0]
print(f"FALSE PASS (gate=PASS but gr.hard_fails>0): {len(false_pass)}")
for p in sorted(false_pass, key=lambda x: x['gr_score']):
    print(f"  {p['name']}: score={p['score']}, gr_score={p['gr_score']}, gr_hard={p['gr_hard']}")
PYEOF
```

## 处理策略

1. **最低分优先**: 按 `gates_result.quality_score` 从低到高排序
2. **每个批次只派一个Codex任务**: 修好一个再派下一个
3. **修复state.json后验证**: 更新后重新扫描确认状态正确
4. **优先修复缺目录的论文**: 02-data/、04-results/等缺失是结构问题

## 已知数据录入错误模式

| 错误 | 原因 | 修复 |
|:-----|:-----|:-----|
| quality_score=0.935 | 小数点错误，应为93.5 | 改为93.5（或从gates_result取值） |
| quality_score=75, gr=25 | 旧pipeline vs 新审计分 | 更新为gr值 |
| gate=PASS, hard_fails=2 | top-level gate未更新 | 改为HARD_FAIL |

## ⚠️ 质量报告有但 state.json 缺失（2026-06-26 实战发现）

**问题**：某些论文目录仅有 `quality_report.md/pdf`（来自质量扫描或审计），但 **没有 `state.json`**。这意味着：
1. 论文被扫描过（有质量报告），但未通过 G1-G7 pipeline 完整集成
2. 这类论文在 cron bulk scan 中被 **完全跳过**（扫描脚本 `for c in [state.json, ...] if not os.path.exists: continue`）
3. 它们可能存在于管线目录中数周甚至数月，从未被正式审计

**检测命令**（在已有 state.json 扫描之前运行）：
```bash
base="/media/yakeworld/sda2/Synthos/outputs/papers"
cd "$base"
for d in */; do
  # 跳过非论文目录和归档
  case "$d" in _archive|AUDIT_QUEUE.md|agent-log.md|paper-queue.json|*) continue;; esac
  if [ -f "${d}quality_report.md" ] && [ ! -f "${d}state.json" ]; then
    echo "ORPHAN_REPORT: $d (has quality report but no state.json)"
    # 进一步检查：是否有 PDF、是否有 01-manuscript 等目录
    ls "${d}*" 2>/dev/null | head -5
  fi
done
```

**修复策略**：
1. **先扫描有 state.json 的论文**（正常流程）
2. **再扫无 state.json 但有质量报告的论文**（新步骤）
3. **对每个 orphan_report**：判断是审计目标（如撤稿论文）还是正常论文
   - 如果是撤稿论文/审计目标 → 保持现状（不需要 state.json）
   - 如果是正常论文 → 需要 G1-G7 pipeline 集成

**实战数据（2026-06-26）**：
| 论文 | 状态 | 判定 |
|:-----|:-----|:-----|
| bmri2022-4085039 | 有报告无state | 温州撤稿论文审计 → 正常 |
| cbt-emdr-2022 | 有报告无state | 温州撤稿论文审计 → 正常 |
| zebrafish-snp-2024 | 有报告无state | 温州撤稿论文审计 → 正常 |
| zheyan-chen-ecoenv-2025 | 有07-quality/deep_review | 温州撤稿论文审计 → 正常 |

> 这4篇是撤稿论文审计产物，无 state.json 是 **预期行为**（它们是审计目标，不是管线论文）。但批量扫描脚本应能区分"预期缺失"和"意外缺失"。
