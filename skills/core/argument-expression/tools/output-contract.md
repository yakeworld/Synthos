---
name: tool-argument-output
category: tool
description: argument-expression 输出契约 — 论据链 JSON、CARS 引言、IMRAD 验证报告
version: 1.0.0
---

# 论证输出契约

> **工程层**：本文档只定义输出交付的工具契约（路径、格式、内容结构）。
> 论证构建逻辑、Toulmin 模型、Hyland 修辞框架见上层 `argument-expression/SKILL.md`（哲学层）。

## 输出交付（Step 7）

```bash
mkdir -p outputs/{session}/
# 论据链 JSON
python3 -c "import json; json.dump(arg_chain, open('outputs/{session}/arguments.json','w'), indent=2, ensure_ascii=False)"
# CARS 引言草案
cat > outputs/{session}/introduction_draft.md << 'EOF'
... CARS 三步生成的引言 ...
EOF
# IMRAD 验证报告
cat > outputs/{session}/imrad_report.md << 'EOF'
... IMRAD各节检查结果 ...
EOF
```

## 产出清单

| 文件 | 格式 | 内容 |
|------|------|------|
| `outputs/{session}/arguments.json` | JSON (UTF-8, indent=2) | 论据链（Toulmin 结构：claim/data/warrant/backing/qualifier/rebuttal） |
| `outputs/{session}/introduction_draft.md` | Markdown | CARS 三步引言草案 |
| `outputs/{session}/imrad_report.md` | Markdown | IMRAD 各节检查结果 |

## 错误处理

| 症状 | 处置 |
|------|------|
| 输出目录不存在 | 先 `mkdir -p outputs/{session}/` |
| JSON 中文乱码 | 必须 `ensure_ascii=False` |
