# Codex G1-G7 论文质量检查工作流

> 2026-06-24 实战确认。通过 tmux Codex 对 pima-crispdm 论文运行完整 G1-G7 检查，耗时约 2 分钟，产出 291 行质量报告。

## 触发条件

论文完成初步编译后、投稿前，需要独立的质量审计。

## 工作流

### 第一步：准备任务描述

写入任务文件 `/tmp/codex_quality_check_task.md`，包含：
- 论文位置（完整目录路径）
- G1-G7 检查范围（每项的具体检查内容）
- L0.5 数据诚实门要求
- 三要素评价
- P0/P1/P2 优先级标注
- 输出文件路径（/tmp/paper_quality_report.md + /tmp/paper_fix_recommendations.md）

### 第二步：通过 tmux 发送给 Codex

```bash
# 发送指令（分两步）
tmux send-keys -t codex-<session> '请读取 /tmp/codex_quality_check_task.md 并执行'
tmux send-keys -t codex-<session> Enter

# 等待执行
sleep 60
tmux capture-pane -t codex-<session> -p -S -20 | tail -20

# 重复等待直到出现提示符
```

### 第三步：读取输出文件

检查 `/tmp/paper_quality_report.md` 和 `/tmp/paper_fix_recommendations.md`。

### 第四步：应用 P0 修复

按优先级修复。P0 问题必须立即修复。典型 P0 发现：
- Cohen's d 计算错误
- Ensemble 结果混用（成员不一致）
- 无引用的数值声明
- 虚构参考文献

### 第五步：重编译验证

```bash
rm -f *.aux *.bbl *.blg *.out *.spl
pdflatex → bibtex → pdflatex → pdflatex
grep "Overfull.*hbox" paper.log  # 应 = 0
grep -c "Error" paper.log         # 应 = 0
```

## 参考案例

PIMA pima-crispdm 2026-06-24:
- 质量评分: 87.9/100
- L0.5 数据诚实门: 82/100 (未通过，因 ensemble 混用)
- P0 发现: Cohen's d, Ensemble std, 无引用声明
- 修复后: 15 页, 0 Overfull, 0 Error
